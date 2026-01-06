# OpenVPN Access Server Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "OpenVPN Access Server (VPN)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "vpn.example.com"},
    {"name": "port", "type": "text", "label": "Admin Port", "default": "943"},
    {"name": "username", "type": "text", "label": "Username", "default": "openvpn"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "openvpn / (set during setup). Admin: 943, VPN: 443/1194"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to OpenVPN Access Server admin interface.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '943').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    base_url = f"https://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # Try admin web login
        login_url = f"{base_url}/admin/__session_start__/"
        login_data = {
            "username": username,
            "password": password
        }
        
        response = session.post(login_url, data=login_data, timeout=15)
        
        if response.status_code == 200:
            # Check for admin session
            if "__session__" in response.text or "admin" in response.url:
                # Get version info
                status_url = f"{base_url}/admin/status_overview"
                status_resp = session.get(status_url, timeout=10)
                
                version = "unknown"
                if status_resp.status_code == 200:
                    import re
                    ver_match = re.search(r'OpenVPN-AS["\s:]+([0-9.]+)', status_resp.text)
                    if ver_match:
                        version = ver_match.group(1)
                
                return True, f"Successfully authenticated to OpenVPN Access Server at {host}\nVersion: {version}"
            elif "Invalid" in response.text or "failed" in response.text.lower():
                return False, "Authentication failed: Invalid credentials"
        
        # Try API auth
        api_url = f"{base_url}/RPC2"
        import base64
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers = {"Authorization": f"Basic {credentials}"}
        
        response = session.get(api_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return True, f"Successfully authenticated to OpenVPN at {host}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"OpenVPN error: {e}"

