# Metabase Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Metabase (Analytics)"

form_fields = [
    {"name": "url", "type": "text", "label": "Metabase URL"},
    {"name": "username", "type": "text", "label": "Email"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "api_key", "type": "password", "label": "API Key (Alternative)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default port 3000. API key from Admin > Settings > Authentication."},
]


def authenticate(form_data):
    """Attempt to authenticate to Metabase."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    api_key = form_data.get('api_key', '').strip()
    
    if not url:
        return False, "Metabase URL is required"
    
    if not url.startswith('http'):
        url = f"http://{url}"
    url = url.rstrip('/')
    
    try:
        session = requests.Session()
        
        if api_key:
            headers = {'x-api-key': api_key}
        else:
            if not username:
                return False, "Email or API Key required"
            
            # Login
            login_resp = session.post(f"{url}/api/session",
                                     json={'username': username, 'password': password},
                                     timeout=15)
            
            if login_resp.status_code == 200:
                headers = {}
            else:
                return False, f"Login failed: {login_resp.status_code}"
        
        # Get current user
        response = session.get(f"{url}/api/user/current",
                              headers=headers, timeout=15)
        
        if response.status_code == 200:
            user = response.json()
            user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            email = user.get('email', 'unknown')
            is_superuser = user.get('is_superuser', False)
            
            # Get database count
            db_resp = session.get(f"{url}/api/database",
                                 headers=headers, timeout=10)
            db_count = 0
            if db_resp.status_code == 200:
                db_count = len(db_resp.json().get('data', db_resp.json()) if isinstance(db_resp.json(), dict) else db_resp.json())
            
            # Get dashboard count
            dash_resp = session.get(f"{url}/api/dashboard",
                                   headers=headers, timeout=10)
            dash_count = 0
            if dash_resp.status_code == 200:
                dash_count = len(dash_resp.json())
            
            role = "Superuser" if is_superuser else "User"
            return True, f"Successfully authenticated to Metabase\nUser: {user_name} ({email})\nRole: {role}\nDatabases: {db_count}\nDashboards: {dash_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Metabase error: {e}"

