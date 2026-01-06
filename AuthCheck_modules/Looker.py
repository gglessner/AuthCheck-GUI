# Looker Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Looker (Analytics)"

form_fields = [
    {"name": "base_url", "type": "text", "label": "Looker URL"},
    {"name": "client_id", "type": "text", "label": "Client ID"},
    {"name": "client_secret", "type": "password", "label": "Client Secret"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API credentials from Admin > Users > API3 Keys. URL format: xxx.looker.com or xxx.cloud.looker.com"},
]


def authenticate(form_data):
    """Attempt to authenticate to Looker."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    base_url = form_data.get('base_url', '').strip()
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '')
    
    if not base_url:
        return False, "Looker URL is required"
    if not client_id:
        return False, "Client ID is required"
    if not client_secret:
        return False, "Client Secret is required"
    
    if not base_url.startswith('http'):
        base_url = f"https://{base_url}"
    base_url = base_url.rstrip('/')
    
    try:
        # Get access token
        token_resp = requests.post(f"{base_url}/api/4.0/login",
                                  data={'client_id': client_id, 'client_secret': client_secret},
                                  timeout=15)
        
        if token_resp.status_code == 200:
            access_token = token_resp.json().get('access_token')
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Get current user
            user_resp = requests.get(f"{base_url}/api/4.0/user",
                                    headers=headers, timeout=10)
            user_name = 'unknown'
            if user_resp.status_code == 200:
                user = user_resp.json()
                user_name = user.get('display_name', user.get('email', 'unknown'))
            
            # Get look count
            looks_resp = requests.get(f"{base_url}/api/4.0/looks",
                                     headers=headers, timeout=10)
            look_count = 0
            if looks_resp.status_code == 200:
                look_count = len(looks_resp.json())
            
            # Get dashboard count
            dashboards_resp = requests.get(f"{base_url}/api/4.0/dashboards",
                                          headers=headers, timeout=10)
            dashboard_count = 0
            if dashboards_resp.status_code == 200:
                dashboard_count = len(dashboards_resp.json())
            
            # Get connection count
            connections_resp = requests.get(f"{base_url}/api/4.0/connections",
                                           headers=headers, timeout=10)
            connection_count = 0
            if connections_resp.status_code == 200:
                connection_count = len(connections_resp.json())
            
            # Logout
            requests.delete(f"{base_url}/api/4.0/logout", headers=headers, timeout=5)
            
            return True, f"Successfully authenticated to Looker\nUser: {user_name}\nDashboards: {dashboard_count}\nLooks: {look_count}\nConnections: {connection_count}"
        elif token_resp.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {token_resp.status_code}: {token_resp.text[:200]}"
            
    except Exception as e:
        return False, f"Looker error: {e}"

