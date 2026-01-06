# Auth0 Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Auth0 (IAM)"

form_fields = [
    {"name": "domain", "type": "text", "label": "Auth0 Domain"},
    {"name": "client_id", "type": "text", "label": "Client ID"},
    {"name": "client_secret", "type": "password", "label": "Client Secret"},
    {"name": "audience", "type": "text", "label": "API Audience", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Domain: xxx.auth0.com or xxx.us.auth0.com. From Applications > Settings."},
]


def authenticate(form_data):
    """Attempt to authenticate to Auth0."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    domain = form_data.get('domain', '').strip()
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '')
    audience = form_data.get('audience', '').strip()
    
    if not domain:
        return False, "Auth0 Domain is required"
    if not client_id:
        return False, "Client ID is required"
    if not client_secret:
        return False, "Client Secret is required"
    
    # Normalize domain
    if not domain.startswith('http'):
        domain = f"https://{domain}"
    domain = domain.rstrip('/')
    
    try:
        # Get access token
        token_url = f"{domain}/oauth/token"
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'audience': audience if audience else f"{domain}/api/v2/"
        }
        
        response = requests.post(token_url, json=token_data, timeout=15)
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            
            headers = {'Authorization': f'Bearer {token}'}
            
            # Get tenant info
            tenant_resp = requests.get(f"{domain}/api/v2/tenants/settings",
                                       headers=headers, timeout=10)
            tenant_name = 'unknown'
            if tenant_resp.status_code == 200:
                tenant_name = tenant_resp.json().get('friendly_name', 'unknown')
            
            # Get user count
            users_resp = requests.get(f"{domain}/api/v2/users?per_page=1&include_totals=true",
                                     headers=headers, timeout=10)
            user_count = 0
            if users_resp.status_code == 200:
                user_count = users_resp.json().get('total', 0)
            
            # Get application count
            apps_resp = requests.get(f"{domain}/api/v2/clients",
                                    headers=headers, timeout=10)
            app_count = 0
            if apps_resp.status_code == 200:
                app_count = len(apps_resp.json())
            
            return True, f"Successfully authenticated to Auth0\nTenant: {tenant_name}\nUsers: {user_count}\nApplications: {app_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Authentication failed: Invalid audience or insufficient permissions"
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('error_description', error_data.get('error', response.text[:200]))
            except:
                error_msg = response.text[:200]
            return False, f"Authentication failed: {error_msg}"
            
    except Exception as e:
        return False, f"Auth0 error: {e}"

