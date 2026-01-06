# EnGenius Cloud Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "EnGenius Cloud (Wireless)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.0.1"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "mode", "type": "combo", "label": "Mode",
     "options": ["Standalone AP", "Cloud (EnGenius Cloud)", "ezMaster"]},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Standalone: admin / admin. Cloud: cloud.engenius.ai"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to EnGenius device or cloud.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    mode = form_data.get('mode', 'Standalone AP')
    use_https = form_data.get('use_https', True)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    scheme = "https" if use_https else "http"
    base_url = f"{scheme}://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        if mode == "Cloud (EnGenius Cloud)":
            # EnGenius Cloud API
            login_url = "https://cloud.engenius.ai/api/v1/auth/login"
            login_data = {
                "email": username,
                "password": password
            }
            
            response = session.post(login_url, json=login_data, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('token') or data.get('access_token'):
                    return True, f"Successfully authenticated to EnGenius Cloud"
                else:
                    return False, "Login failed: No token received"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
                
        elif mode == "ezMaster":
            # ezMaster controller
            login_url = f"{base_url}/api/login"
            login_data = {
                "username": username,
                "password": password
            }
            
            response = session.post(login_url, json=login_data, timeout=15)
            
            if response.status_code == 200:
                return True, f"Successfully authenticated to ezMaster at {host}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
                
        else:  # Standalone AP
            login_url = f"{base_url}/cgi-bin/luci"
            login_data = {
                "luci_username": username,
                "luci_password": password
            }
            
            response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
            
            if response.status_code == 200:
                if "logout" in response.text.lower() or "status" in response.text.lower():
                    return True, f"Successfully authenticated to EnGenius AP at {host}"
                elif "invalid" in response.text.lower():
                    return False, "Authentication failed: Invalid credentials"
            
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"EnGenius error: {e}"

