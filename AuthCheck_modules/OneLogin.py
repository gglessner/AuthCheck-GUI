# OneLogin Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "OneLogin (IAM)"

form_fields = [
    {"name": "region", "type": "combo", "label": "Region", "options": ["US", "EU"], "default": "US"},
    {"name": "client_id", "type": "text", "label": "Client ID"},
    {"name": "client_secret", "type": "password", "label": "Client Secret"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API credentials from Administration > Developers > API Credentials."},
]


def authenticate(form_data):
    """Attempt to authenticate to OneLogin."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    region = form_data.get('region', 'US')
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '')
    
    if not client_id:
        return False, "Client ID is required"
    if not client_secret:
        return False, "Client Secret is required"
    
    try:
        # Regional API URLs
        if region == "EU":
            api_url = "https://api.eu.onelogin.com"
        else:
            api_url = "https://api.us.onelogin.com"
        
        # Get access token
        token_url = f"{api_url}/auth/oauth2/v2/token"
        token_data = {'grant_type': 'client_credentials'}
        
        response = requests.post(token_url, data=token_data,
                                auth=(client_id, client_secret), timeout=15)
        
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get user count
            users_resp = requests.get(f"{api_url}/api/2/users",
                                     headers=headers, timeout=10)
            user_count = 0
            if users_resp.status_code == 200:
                user_count = len(users_resp.json())
            
            # Get app count
            apps_resp = requests.get(f"{api_url}/api/2/apps",
                                    headers=headers, timeout=10)
            app_count = 0
            if apps_resp.status_code == 200:
                app_count = len(apps_resp.json())
            
            # Get role count
            roles_resp = requests.get(f"{api_url}/api/2/roles",
                                     headers=headers, timeout=10)
            role_count = 0
            if roles_resp.status_code == 200:
                role_count = len(roles_resp.json())
            
            return True, f"Successfully authenticated to OneLogin\nRegion: {region}\nUsers: {user_count}\nApps: {app_count}\nRoles: {role_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('message', response.text[:200])
            except:
                error_msg = response.text[:200]
            return False, f"Authentication failed: {error_msg}"
            
    except Exception as e:
        return False, f"OneLogin error: {e}"

