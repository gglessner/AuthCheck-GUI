# Cribl Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Cribl Stream (Logging)"

form_fields = [
    {"name": "host", "type": "text", "label": "Cribl Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "9000"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "auth_token", "type": "password", "label": "Auth Token (Alternative)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: admin/admin. Port 9000. Auth token from Settings > Auth Tokens."},
]


def authenticate(form_data):
    """Attempt to authenticate to Cribl Stream."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '9000').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    auth_token = form_data.get('auth_token', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Cribl Host is required"
    
    try:
        base_url = f"https://{host}:{port}"
        session = requests.Session()
        session.verify = verify_ssl
        
        if auth_token:
            headers = {'Authorization': f'Bearer {auth_token}'}
        else:
            if not username:
                return False, "Username or Auth Token required"
            
            # Login
            login_resp = session.post(
                f"{base_url}/api/v1/auth/login",
                json={'username': username, 'password': password},
                timeout=15
            )
            
            if login_resp.status_code != 200:
                return False, "Authentication failed: Invalid credentials"
            
            token = login_resp.json().get('token')
            headers = {'Authorization': f'Bearer {token}'}
        
        # Get system info
        response = session.get(
            f"{base_url}/api/v1/system/info",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            info = response.json()
            version = info.get('version', 'unknown')
            build = info.get('build', 'unknown')
            
            # Get workers
            workers_resp = session.get(
                f"{base_url}/api/v1/workers",
                headers=headers,
                timeout=10
            )
            worker_count = 0
            if workers_resp.status_code == 200:
                workers = workers_resp.json().get('items', [])
                worker_count = len(workers)
            
            return True, f"Successfully authenticated to Cribl Stream\nHost: {host}:{port}\nVersion: {version}\nBuild: {build}\nWorkers: {worker_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Cribl error: {e}"

