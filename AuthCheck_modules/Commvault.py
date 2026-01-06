# Commvault Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Commvault (Backup)"

form_fields = [
    {"name": "host", "type": "text", "label": "CommServe/Webconsole Host"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / (set during install). REST API on WebConsole. Domain users: DOMAIN\\user."},
]


def authenticate(form_data):
    """Attempt to authenticate to Commvault."""
    try:
        import requests
        import base64
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    username = form_data.get('username', 'admin').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "CommServe/Webconsole Host is required"
    if not username:
        return False, "Username is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # Login
        login_url = f"{host}/webconsole/api/Login"
        
        # Encode password in base64
        encoded_password = base64.b64encode(password.encode()).decode()
        
        login_data = {
            'mode': 4,
            'username': username,
            'password': encoded_password
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = session.post(login_url, json=login_data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'token' in data:
                token = data['token']
                
                headers['Authtoken'] = token
                
                # Get CommCell info
                commcell_resp = session.get(f"{host}/webconsole/api/CommCell",
                                           headers=headers, timeout=10)
                commcell_name = 'unknown'
                if commcell_resp.status_code == 200:
                    cc_data = commcell_resp.json()
                    commcell_name = cc_data.get('commcell', {}).get('commCellName', 'unknown')
                
                # Get client count
                clients_resp = session.get(f"{host}/webconsole/api/Client",
                                          headers=headers, timeout=10)
                client_count = 0
                if clients_resp.status_code == 200:
                    clients = clients_resp.json().get('clientProperties', [])
                    client_count = len(clients)
                
                # Get storage policy count
                sp_resp = session.get(f"{host}/webconsole/api/StoragePolicy",
                                     headers=headers, timeout=10)
                sp_count = 0
                if sp_resp.status_code == 200:
                    sp_count = len(sp_resp.json().get('policies', []))
                
                # Logout
                session.post(f"{host}/webconsole/api/Logout", headers=headers, timeout=5)
                
                return True, f"Successfully authenticated to Commvault\nCommCell: {commcell_name}\nClients: {client_count}\nStorage Policies: {sp_count}"
            else:
                error_msg = data.get('errList', [{}])[0].get('errLogMessage', 'Login failed')
                return False, f"Authentication failed: {error_msg}"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Commvault error: {e}"

