# SaltStack Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "SaltStack (CI/CD)"

form_fields = [
    {"name": "host", "type": "text", "label": "Salt API Host"},
    {"name": "port", "type": "text", "label": "Salt API Port", "default": "8000"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "eauth", "type": "combo", "label": "External Auth", "options": ["pam", "ldap", "auto"], "default": "pam"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Salt API (cherrypy/tornado) on port 8000. PAM auth uses system users."},
]


def authenticate(form_data):
    """Attempt to authenticate to SaltStack API."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8000').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    eauth = form_data.get('eauth', 'pam')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Salt API Host is required"
    if not username:
        return False, "Username is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # Login
        login_resp = session.post(
            f"{host}:{port}/login",
            json={'username': username, 'password': password, 'eauth': eauth},
            timeout=15
        )
        
        if login_resp.status_code == 200:
            data = login_resp.json()
            token = data.get('return', [{}])[0].get('token')
            
            if not token:
                return False, "Login succeeded but no token received"
            
            headers = {'X-Auth-Token': token}
            
            # Get minion count
            minions_resp = session.post(
                f"{host}:{port}/",
                headers=headers,
                json={'client': 'local', 'tgt': '*', 'fun': 'test.ping'},
                timeout=15
            )
            minion_count = 0
            if minions_resp.status_code == 200:
                result = minions_resp.json().get('return', [{}])[0]
                minion_count = len(result)
            
            # Get keys
            keys_resp = session.post(
                f"{host}:{port}/",
                headers=headers,
                json={'client': 'wheel', 'fun': 'key.list_all'},
                timeout=10
            )
            accepted_keys = 0
            pending_keys = 0
            if keys_resp.status_code == 200:
                keys = keys_resp.json().get('return', [{}])[0].get('data', {}).get('return', {})
                accepted_keys = len(keys.get('minions', []))
                pending_keys = len(keys.get('minions_pre', []))
            
            return True, f"Successfully authenticated to SaltStack\nResponding Minions: {minion_count}\nAccepted Keys: {accepted_keys}\nPending Keys: {pending_keys}"
        elif login_resp.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {login_resp.status_code}: {login_resp.text[:200]}"
            
    except Exception as e:
        return False, f"SaltStack error: {e}"

