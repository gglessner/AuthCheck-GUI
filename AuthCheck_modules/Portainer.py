# Portainer Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Portainer (Container)"

form_fields = [
    {"name": "url", "type": "text", "label": "Portainer URL"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "api_key", "type": "password", "label": "API Key (Alternative)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / (set during initial setup). Default ports: 9000 (HTTP), 9443 (HTTPS)."},
]


def authenticate(form_data):
    """Attempt to authenticate to Portainer."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    api_key = form_data.get('api_key', '').strip()
    
    if not url:
        return False, "Portainer URL is required"
    
    if not url.startswith('http'):
        url = f"https://{url}"
    url = url.rstrip('/')
    
    try:
        session = requests.Session()
        
        if api_key:
            headers = {'X-API-Key': api_key}
        else:
            if not username:
                return False, "Username or API Key is required"
            
            # Login
            login_data = {'username': username, 'password': password}
            login_resp = session.post(f"{url}/api/auth",
                                     json=login_data, timeout=15)
            
            if login_resp.status_code == 200:
                jwt = login_resp.json().get('jwt')
                headers = {'Authorization': f'Bearer {jwt}'}
            else:
                return False, f"Login failed: {login_resp.status_code}"
        
        # Get status
        status_resp = session.get(f"{url}/api/status", headers=headers, timeout=10)
        version = 'unknown'
        if status_resp.status_code == 200:
            version = status_resp.json().get('Version', 'unknown')
        
        # Get endpoint count
        endpoints_resp = session.get(f"{url}/api/endpoints", headers=headers, timeout=10)
        endpoint_count = 0
        if endpoints_resp.status_code == 200:
            endpoint_count = len(endpoints_resp.json())
        
        # Get user count
        users_resp = session.get(f"{url}/api/users", headers=headers, timeout=10)
        user_count = 0
        if users_resp.status_code == 200:
            user_count = len(users_resp.json())
        
        return True, f"Successfully authenticated to Portainer {version}\nEndpoints: {endpoint_count}\nUsers: {user_count}"
        
    except Exception as e:
        return False, f"Portainer error: {e}"

