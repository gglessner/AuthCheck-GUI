# NetApp SAN/E-Series Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "NetApp SAN/E-Series (Storage)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.100"},
    {"name": "port", "type": "text", "label": "Port", "default": "8443"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / (set during setup). HTTPS: 8443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to NetApp SAN/E-Series SANtricity.
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
        
        # SANtricity REST API login
        login_url = f"{base_url}/devmgr/utils/login"
        headers = {"Content-Type": "application/json"}
        login_data = {
            "userId": username,
            "password": password
        }
        
        import json
        response = session.post(login_url, data=json.dumps(login_data), headers=headers, timeout=15)
        
        if response.status_code == 200 or response.status_code == 204:
            # Get storage systems
            storage_url = f"{base_url}/devmgr/v2/storage-systems"
            storage_resp = session.get(storage_url, headers=headers, timeout=10)
            
            systems = 0
            if storage_resp.status_code == 200:
                systems = len(storage_resp.json())
            
            return True, f"Successfully authenticated to NetApp SANtricity at {host}\nStorage Systems: {systems}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"NetApp SAN error: {e}"

