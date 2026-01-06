# Drobo NAS Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Drobo (NAS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.100"},
    {"name": "port", "type": "text", "label": "Port", "default": "5000"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / (blank or set). HTTP: 5000"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Drobo NAS.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '5000').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    base_url = f"http://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # Drobo Dashboard API
        login_url = f"{base_url}/ESALogin"
        login_data = {
            "username": username,
            "password": password
        }
        
        response = session.post(login_url, data=login_data, timeout=15)
        
        if response.status_code == 200:
            if "token" in response.text.lower() or "session" in response.text.lower():
                # Get Drobo info
                info_url = f"{base_url}/ESAGetDeviceInfo"
                info_resp = session.get(info_url, timeout=10)
                
                model = "Drobo"
                if info_resp.status_code == 200:
                    import re
                    model_match = re.search(r'model["\s:]+([^"<\s,]+)', info_resp.text, re.IGNORECASE)
                    if model_match:
                        model = model_match.group(1)
                
                return True, f"Successfully authenticated to {model} at {host}"
            elif "invalid" in response.text.lower():
                return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Drobo error: {e}"

