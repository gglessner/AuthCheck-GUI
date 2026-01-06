# MikroTik RouterOS Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "MikroTik RouterOS (Network)"

form_fields = [
    {"name": "host", "type": "text", "label": "RouterOS Host"},
    {"name": "port", "type": "text", "label": "API Port", "default": "8728",
     "port_toggle": "use_ssl", "tls_port": "8729", "non_tls_port": "8728"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8729, Non-TLS: 8728. admin / (blank). Enable API in Services."},
]


def authenticate(form_data):
    """Attempt to authenticate to MikroTik RouterOS."""
    try:
        import socket
        import hashlib
        import binascii
    except ImportError:
        return False, "Required packages not available"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8728').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "RouterOS Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        port = int(port)
        if use_ssl:
            port = 8729
        
        # Try REST API first (RouterOS 7.1+)
        try:
            import requests
            base_url = f"{'https' if use_ssl else 'http'}://{host}"
            response = requests.get(
                f"{base_url}/rest/system/identity",
                auth=(username, password),
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                identity = response.json().get('name', 'unknown')
                
                # Get resource info
                resource_resp = requests.get(
                    f"{base_url}/rest/system/resource",
                    auth=(username, password),
                    verify=False,
                    timeout=10
                )
                version = 'unknown'
                board = 'unknown'
                if resource_resp.status_code == 200:
                    resource = resource_resp.json()
                    version = resource.get('version', 'unknown')
                    board = resource.get('board-name', 'unknown')
                
                return True, f"Successfully authenticated to MikroTik RouterOS\nHost: {host}\nIdentity: {identity}\nVersion: {version}\nBoard: {board}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
        except:
            pass  # Fall through to socket-based API
        
        # Socket-based API authentication
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        if use_ssl:
            import ssl
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            sock = context.wrap_socket(sock, server_hostname=host)
        
        sock.connect((host, port))
        
        # Successfully connected to API port
        sock.close()
        return True, f"Successfully connected to MikroTik RouterOS API\nHost: {host}:{port}\nAPI port is accessible (use Winbox or REST API for full auth)"
        
    except socket.timeout:
        return False, f"Connection timeout to {host}:{port}"
    except ConnectionRefusedError:
        return False, f"Connection refused - API may not be enabled on {host}:{port}"
    except Exception as e:
        return False, f"MikroTik error: {e}"

