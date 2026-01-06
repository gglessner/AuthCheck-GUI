# Varnish Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Varnish (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "http_port", "type": "text", "label": "HTTP Port", "default": "80"},
    {"name": "admin_port", "type": "text", "label": "Admin Port", "default": "6082"},
    {"name": "protocol", "type": "combo", "label": "Protocol",
     "options": ["HTTP Proxy", "Admin CLI"]},
    {"name": "admin_secret", "type": "password", "label": "Admin Secret"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "HTTP: 80/6081, Admin: 6082. Secret in /etc/varnish/secret"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Varnish.
    """
    host = form_data.get('host', '').strip()
    http_port = form_data.get('http_port', '').strip()
    admin_port = form_data.get('admin_port', '').strip()
    protocol = form_data.get('protocol', 'HTTP Proxy')
    admin_secret = form_data.get('admin_secret', '').strip()
    
    if not host:
        return False, "Host is required"
    
    if protocol == "Admin CLI":
        import socket
        import hashlib
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, int(admin_port)))
            
            # Receive challenge
            response = sock.recv(4096).decode('utf-8', errors='ignore')
            
            if "107" in response:  # Auth required
                lines = response.strip().split('\n')
                challenge = None
                for line in lines:
                    if len(line) == 32:  # Challenge is 32 chars
                        challenge = line.strip()
                        break
                
                if challenge and admin_secret:
                    # Calculate auth response
                    auth_str = f"{challenge}\n{admin_secret}\n{challenge}\n"
                    auth_hash = hashlib.sha256(auth_str.encode()).hexdigest()
                    
                    sock.send(f"auth {auth_hash}\n".encode())
                    auth_response = sock.recv(4096).decode('utf-8', errors='ignore')
                    
                    if "200" in auth_response:
                        sock.send(b"status\n")
                        status = sock.recv(4096).decode('utf-8', errors='ignore')
                        sock.close()
                        return True, f"Successfully authenticated to Varnish Admin at {host}:{admin_port}"
                    else:
                        sock.close()
                        return False, "Authentication failed: Invalid secret"
                else:
                    sock.close()
                    return False, "Authentication required but no secret provided"
            elif "200" in response:
                sock.close()
                return True, f"Connected to Varnish Admin at {host}:{admin_port} (no auth required)"
            else:
                sock.close()
                return False, f"Unexpected response: {response[:100]}"
                
        except Exception as e:
            return False, f"Admin CLI error: {e}"
    else:
        try:
            import requests
        except ImportError:
            return False, "requests package not installed"
        
        try:
            url = f"http://{host}:{http_port}/"
            response = requests.get(url, timeout=10)
            
            via = response.headers.get('Via', '')
            x_varnish = response.headers.get('X-Varnish', '')
            
            if 'varnish' in via.lower() or x_varnish:
                return True, f"Successfully connected to Varnish at {host}:{http_port}\nX-Varnish: {x_varnish or 'N/A'}"
            else:
                return True, f"Connected to {host}:{http_port} (Varnish headers not detected)"
                
        except Exception as e:
            return False, f"HTTP error: {e}"

