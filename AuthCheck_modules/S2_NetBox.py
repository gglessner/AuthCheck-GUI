# S2 NetBox Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "S2 NetBox (Access Control)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.100"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / admin (default). HTTPS: 443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to S2 NetBox access control.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
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
        
        # S2 NetBox web login
        login_url = f"{base_url}/goforms/nblogin"
        login_data = {
            "Username": username,
            "Password": password,
            "Submit": "Login"
        }
        
        response = session.post(login_url, data=login_data, timeout=15)
        
        if response.status_code == 200:
            if "logout" in response.text.lower() or "dashboard" in response.text.lower():
                import re
                
                version = "unknown"
                ver_match = re.search(r'NetBox["\s:]+([0-9.]+)', response.text)
                if ver_match:
                    version = ver_match.group(1)
                
                return True, f"Successfully authenticated to S2 NetBox at {host}\nVersion: {version}"
            elif "invalid" in response.text.lower() or "failed" in response.text.lower():
                return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"S2 NetBox error: {e}"

