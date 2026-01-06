# Rancher Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Rancher (Container)"

form_fields = [
    {"name": "url", "type": "text", "label": "Rancher URL"},
    {"name": "access_key", "type": "text", "label": "Access Key"},
    {"name": "secret_key", "type": "password", "label": "Secret Key"},
    {"name": "token", "type": "password", "label": "Bearer Token (Alternative)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API Keys from User Avatar > API & Keys. admin / (set during bootstrap)."},
]


def authenticate(form_data):
    """Attempt to authenticate to Rancher."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', '').strip()
    access_key = form_data.get('access_key', '').strip()
    secret_key = form_data.get('secret_key', '')
    token = form_data.get('token', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not url:
        return False, "Rancher URL is required"
    
    if not url.startswith('http'):
        url = f"https://{url}"
    url = url.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        if token:
            headers = {'Authorization': f'Bearer {token}'}
        elif access_key and secret_key:
            session.auth = (access_key, secret_key)
            headers = {}
        else:
            return False, "Bearer Token or Access Key/Secret Key required"
        
        # Get user info
        response = session.get(f"{url}/v3/users?me=true", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            users = data.get('data', [])
            
            user_name = 'unknown'
            if users:
                user_name = users[0].get('username', users[0].get('name', 'unknown'))
            
            # Get cluster count
            clusters_resp = session.get(f"{url}/v3/clusters", headers=headers, timeout=10)
            cluster_count = 0
            if clusters_resp.status_code == 200:
                cluster_count = len(clusters_resp.json().get('data', []))
            
            # Get Rancher version
            settings_resp = session.get(f"{url}/v3/settings/server-version", headers=headers, timeout=10)
            version = 'unknown'
            if settings_resp.status_code == 200:
                version = settings_resp.json().get('value', 'unknown')
            
            return True, f"Successfully authenticated to Rancher {version}\nUser: {user_name}\nManaged Clusters: {cluster_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Rancher error: {e}"

