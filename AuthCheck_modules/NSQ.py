# NSQ Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "NSQ (MQ)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "nsqd_tcp_port", "type": "text", "label": "nsqd TCP Port", "default": "4150",
     "port_toggle": "use_tls", "tls_port": "4152", "non_tls_port": "4150"},
    {"name": "nsqd_http_port", "type": "text", "label": "nsqd HTTP Port", "default": "4151"},
    {"name": "nsqlookupd_port", "type": "text", "label": "nsqlookupd Port", "default": "4161"},
    {"name": "protocol", "type": "combo", "label": "Protocol",
     "options": ["TCP (nsqd)", "HTTP (nsqd)", "HTTP (nsqlookupd)"]},
    {"name": "use_tls", "type": "checkbox", "label": "Enable TLS"},
    {"name": "auth_secret", "type": "password", "label": "Auth Secret"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "nsqd TCP: 4150/4152, HTTP: 4151. nsqlookupd: 4161. Default: no auth"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to NSQ.
    """
    host = form_data.get('host', '').strip()
    nsqd_tcp_port = form_data.get('nsqd_tcp_port', '').strip()
    nsqd_http_port = form_data.get('nsqd_http_port', '').strip()
    nsqlookupd_port = form_data.get('nsqlookupd_port', '').strip()
    protocol = form_data.get('protocol', 'TCP (nsqd)')
    use_tls = form_data.get('use_tls', False)
    auth_secret = form_data.get('auth_secret', '').strip()
    
    if not host:
        return False, "Host is required"
    
    if "HTTP" in protocol:
        try:
            import requests
        except ImportError:
            return False, "requests package not installed"
        
        scheme = "https" if use_tls else "http"
        
        if "nsqlookupd" in protocol:
            port = nsqlookupd_port
            url = f"{scheme}://{host}:{port}/topics"
        else:
            port = nsqd_http_port
            url = f"{scheme}://{host}:{port}/ping"
        
        try:
            headers = {}
            if auth_secret:
                headers['Authorization'] = f"Bearer {auth_secret}"
            
            response = requests.get(url, headers=headers, verify=False, timeout=10)
            
            if response.status_code == 200:
                return True, f"Successfully connected to NSQ at {host}:{port}"
            elif response.status_code == 401 or response.status_code == 403:
                return False, "Authentication failed: Invalid auth secret"
            else:
                return False, f"NSQ returned status {response.status_code}"
        except Exception as e:
            return False, f"NSQ HTTP error: {e}"
    else:
        import socket
        import ssl
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            if use_tls:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=host)
            
            sock.connect((host, int(nsqd_tcp_port)))
            
            # NSQ protocol version
            sock.send(b"  V2")
            
            # IDENTIFY command
            import json
            identify_data = json.dumps({
                "client_id": "authcheck",
                "hostname": "authcheck",
                "feature_negotiation": True,
            }).encode()
            
            if auth_secret:
                identify_data = json.dumps({
                    "client_id": "authcheck",
                    "hostname": "authcheck",
                    "feature_negotiation": True,
                    "auth_secret": auth_secret,
                }).encode()
            
            cmd = f"IDENTIFY\n".encode() + len(identify_data).to_bytes(4, 'big') + identify_data
            sock.send(cmd)
            
            response = sock.recv(4096)
            sock.close()
            
            if b"OK" in response or b"feature_negotiation" in response:
                return True, f"Successfully connected to NSQ at {host}:{nsqd_tcp_port}"
            elif b"E_UNAUTHORIZED" in response or b"AUTH" in response:
                return False, "Authentication failed: Invalid auth secret"
            else:
                return True, f"Connected to NSQ at {host}:{nsqd_tcp_port}"
                
        except Exception as e:
            return False, f"NSQ TCP error: {e}"

