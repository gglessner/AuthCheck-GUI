# Asterisk/FreePBX Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Asterisk/FreePBX (PBX)"

form_fields = [
    {"name": "host", "type": "text", "label": "Asterisk Host"},
    {"name": "ami_port", "type": "text", "label": "AMI Port", "default": "5038"},
    {"name": "http_port", "type": "text", "label": "HTTP Port (FreePBX)", "default": "80"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["AMI", "FreePBX API", "ARI"], "default": "AMI"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "AMI port 5038. FreePBX default: admin/admin. ARI port 8088."},
]


def authenticate(form_data):
    """Attempt to authenticate to Asterisk/FreePBX."""
    try:
        import requests
        import socket
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    ami_port = form_data.get('ami_port', '5038').strip()
    http_port = form_data.get('http_port', '80').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    auth_type = form_data.get('auth_type', 'AMI')
    
    if not host:
        return False, "Asterisk Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        if auth_type == 'AMI':
            # Asterisk Manager Interface
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, int(ami_port)))
            
            # Read banner
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            
            # Send login
            login_cmd = f"Action: Login\r\nUsername: {username}\r\nSecret: {password}\r\n\r\n"
            sock.send(login_cmd.encode())
            
            response = sock.recv(2048).decode('utf-8', errors='ignore')
            sock.close()
            
            if 'Success' in response or 'Authentication accepted' in response:
                # Extract version from banner
                version = 'unknown'
                if 'Asterisk' in banner:
                    import re
                    ver_match = re.search(r'Asterisk[/ ]*([\d.]+)', banner)
                    if ver_match:
                        version = ver_match.group(1)
                
                return True, f"Successfully authenticated to Asterisk AMI\nHost: {host}:{ami_port}\nVersion: {version}\nAMI: Connected"
            else:
                return False, "Authentication failed: Invalid credentials"
                
        elif auth_type == 'FreePBX API':
            # FreePBX GraphQL API
            base_url = f"http://{host}:{http_port}"
            
            # Try to get token
            token_resp = requests.post(
                f"{base_url}/admin/api/api/token",
                json={'username': username, 'password': password},
                timeout=15
            )
            
            if token_resp.status_code == 200:
                token_data = token_resp.json()
                access_token = token_data.get('access_token', token_data.get('token'))
                
                if access_token:
                    return True, f"Successfully authenticated to FreePBX API\nHost: {host}:{http_port}\nToken obtained"
                else:
                    return False, "No token in response"
            elif token_resp.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            else:
                return False, f"HTTP {token_resp.status_code}"
                
        else:  # ARI
            # Asterisk REST Interface
            ari_url = f"http://{host}:8088/ari/asterisk/info"
            
            response = requests.get(
                ari_url,
                auth=(username, password),
                timeout=15
            )
            
            if response.status_code == 200:
                info = response.json()
                build_info = info.get('build', {})
                version = build_info.get('version', 'unknown')
                
                return True, f"Successfully authenticated to Asterisk ARI\nHost: {host}:8088\nVersion: {version}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            else:
                return False, f"HTTP {response.status_code}"
            
    except socket.timeout:
        return False, f"Connection timeout to {host}"
    except ConnectionRefusedError:
        return False, f"Connection refused on {host}"
    except Exception as e:
        return False, f"Asterisk error: {e}"

