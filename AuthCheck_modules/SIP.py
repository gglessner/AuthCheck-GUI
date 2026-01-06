# SIP Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "SIP (PBX)"

form_fields = [
    {"name": "host", "type": "text", "label": "SIP Server"},
    {"name": "port", "type": "text", "label": "Port", "default": "5060"},
    {"name": "transport", "type": "combo", "label": "Transport", "options": ["UDP", "TCP", "TLS"], "default": "UDP"},
    {"name": "username", "type": "text", "label": "Username/Extension"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "domain", "type": "text", "label": "Domain/Realm"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Standard SIP: 5060 (UDP/TCP), 5061 (TLS). Tests REGISTER auth."},
]


def authenticate(form_data):
    """Attempt to authenticate via SIP REGISTER."""
    import socket
    import hashlib
    import random
    import string
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '5060').strip()
    transport = form_data.get('transport', 'UDP')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    domain = form_data.get('domain', '').strip()
    
    if not host:
        return False, "SIP Server is required"
    if not username:
        return False, "Username is required"
    
    if not domain:
        domain = host
    
    try:
        # Generate call-id and tag
        call_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
        tag = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        branch = 'z9hG4bK' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        
        # Build initial REGISTER request (no auth)
        local_ip = socket.gethostbyname(socket.gethostname())
        
        register_msg = f"""REGISTER sip:{domain} SIP/2.0\r
Via: SIP/2.0/{transport} {local_ip}:5060;branch={branch};rport\r
From: <sip:{username}@{domain}>;tag={tag}\r
To: <sip:{username}@{domain}>\r
Call-ID: {call_id}@{local_ip}\r
CSeq: 1 REGISTER\r
Contact: <sip:{username}@{local_ip}:5060>\r
Max-Forwards: 70\r
Expires: 3600\r
Content-Length: 0\r
\r
"""
        
        if transport == 'UDP':
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if transport == 'TLS':
                import ssl
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=host)
        
        sock.settimeout(10)
        
        if transport != 'UDP':
            sock.connect((host, int(port)))
        
        if transport == 'UDP':
            sock.sendto(register_msg.encode(), (host, int(port)))
            response, addr = sock.recvfrom(4096)
        else:
            sock.send(register_msg.encode())
            response = sock.recv(4096)
        
        response = response.decode('utf-8', errors='ignore')
        
        # Check response
        if 'SIP/2.0 200' in response:
            sock.close()
            return True, f"Successfully authenticated to SIP\nServer: {host}:{port} ({transport})\nUser: {username}@{domain}\nNo authentication required!"
        
        elif 'SIP/2.0 401' in response or 'SIP/2.0 407' in response:
            # Need to authenticate - parse WWW-Authenticate header
            import re
            
            auth_match = re.search(r'WWW-Authenticate:\s*Digest\s+(.+?)(?:\r\n|\n)', response, re.IGNORECASE)
            if not auth_match:
                auth_match = re.search(r'Proxy-Authenticate:\s*Digest\s+(.+?)(?:\r\n|\n)', response, re.IGNORECASE)
            
            if auth_match:
                auth_params = auth_match.group(1)
                
                # Parse realm and nonce
                realm_match = re.search(r'realm="([^"]+)"', auth_params)
                nonce_match = re.search(r'nonce="([^"]+)"', auth_params)
                
                if realm_match and nonce_match:
                    realm = realm_match.group(1)
                    nonce = nonce_match.group(1)
                    
                    # Calculate digest response
                    ha1 = hashlib.md5(f"{username}:{realm}:{password}".encode()).hexdigest()
                    ha2 = hashlib.md5(f"REGISTER:sip:{domain}".encode()).hexdigest()
                    digest_response = hashlib.md5(f"{ha1}:{nonce}:{ha2}".encode()).hexdigest()
                    
                    # Build authenticated REGISTER
                    branch2 = 'z9hG4bK' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
                    
                    auth_register = f"""REGISTER sip:{domain} SIP/2.0\r
Via: SIP/2.0/{transport} {local_ip}:5060;branch={branch2};rport\r
From: <sip:{username}@{domain}>;tag={tag}\r
To: <sip:{username}@{domain}>\r
Call-ID: {call_id}@{local_ip}\r
CSeq: 2 REGISTER\r
Contact: <sip:{username}@{local_ip}:5060>\r
Max-Forwards: 70\r
Expires: 3600\r
Authorization: Digest username="{username}",realm="{realm}",nonce="{nonce}",uri="sip:{domain}",response="{digest_response}",algorithm=MD5\r
Content-Length: 0\r
\r
"""
                    
                    if transport == 'UDP':
                        sock.sendto(auth_register.encode(), (host, int(port)))
                        response2, addr = sock.recvfrom(4096)
                    else:
                        sock.send(auth_register.encode())
                        response2 = sock.recv(4096)
                    
                    response2 = response2.decode('utf-8', errors='ignore')
                    sock.close()
                    
                    if 'SIP/2.0 200' in response2:
                        return True, f"Successfully authenticated to SIP\nServer: {host}:{port} ({transport})\nUser: {username}@{domain}\nRealm: {realm}"
                    elif 'SIP/2.0 401' in response2 or 'SIP/2.0 403' in response2:
                        return False, "Authentication failed: Invalid credentials"
                    else:
                        status_match = re.search(r'SIP/2.0 (\d+)', response2)
                        status = status_match.group(1) if status_match else 'unknown'
                        return False, f"SIP response: {status}"
        
        sock.close()
        
        # Parse status code
        import re
        status_match = re.search(r'SIP/2.0 (\d+)', response)
        status = status_match.group(1) if status_match else 'unknown'
        return False, f"SIP response: {status}"
        
    except socket.timeout:
        return False, f"Connection timeout to {host}:{port}"
    except Exception as e:
        return False, f"SIP error: {e}"

