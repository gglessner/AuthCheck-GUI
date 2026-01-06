# Siemens Desigo CC Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Siemens Desigo CC (BMS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.100"},
    {"name": "port", "type": "text", "label": "Port", "default": "8443"},
    {"name": "username", "type": "text", "label": "Username", "default": "Administrator"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Administrator / Desigo (default). HTTPS: 8443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Siemens Desigo CC.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8443').strip()
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
        
        # Desigo CC API login
        login_url = f"{base_url}/api/authentication/login"
        login_data = {
            "username": username,
            "password": password
        }
        
        headers = {"Content-Type": "application/json"}
        import json
        
        response = session.post(login_url, data=json.dumps(login_data), headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("token") or data.get("success"):
                # Get system info
                info_url = f"{base_url}/api/system/info"
                info_resp = session.get(info_url, headers=headers, timeout=10)
                
                version = "unknown"
                if info_resp.status_code == 200:
                    version = info_resp.json().get("version", "unknown")
                
                return True, f"Successfully authenticated to Desigo CC at {host}\nVersion: {version}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        # Try web login
        login_url = f"{base_url}/DesigoCCWebClient/login"
        login_data = {
            "username": username,
            "password": password
        }
        
        response = session.post(login_url, data=login_data, timeout=15)
        
        if response.status_code == 200 and "dashboard" in response.text.lower():
            return True, f"Successfully authenticated to Desigo CC at {host}"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Desigo CC error: {e}"

