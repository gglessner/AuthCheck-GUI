# AppDynamics Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "AppDynamics (Monitoring)"

form_fields = [
    {"name": "controller_url", "type": "text", "label": "Controller URL"},
    {"name": "account", "type": "text", "label": "Account Name"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "api_client", "type": "text", "label": "API Client Name (OAuth)"},
    {"name": "client_secret", "type": "password", "label": "Client Secret (OAuth)"},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["Basic", "OAuth"], "default": "Basic"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "SaaS: xxx.saas.appdynamics.com. On-prem: controller-host:8090. Default admin user created during setup."},
]


def authenticate(form_data):
    """Attempt to authenticate to AppDynamics."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    controller_url = form_data.get('controller_url', '').strip()
    account = form_data.get('account', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    api_client = form_data.get('api_client', '').strip()
    client_secret = form_data.get('client_secret', '')
    auth_type = form_data.get('auth_type', 'Basic')
    
    if not controller_url:
        return False, "Controller URL is required"
    if not account:
        return False, "Account Name is required"
    
    if not controller_url.startswith('http'):
        controller_url = f"https://{controller_url}"
    controller_url = controller_url.rstrip('/')
    
    try:
        if auth_type == "OAuth":
            if not api_client or not client_secret:
                return False, "API Client Name and Client Secret required for OAuth"
            
            # Get OAuth token
            token_url = f"{controller_url}/controller/api/oauth/access_token"
            token_data = {
                'grant_type': 'client_credentials',
                'client_id': f"{api_client}@{account}",
                'client_secret': client_secret
            }
            token_resp = requests.post(token_url, data=token_data, timeout=10)
            
            if token_resp.status_code != 200:
                return False, f"OAuth token request failed: {token_resp.status_code}"
            
            access_token = token_resp.json().get('access_token')
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(f"{controller_url}/controller/rest/applications",
                                   headers=headers, timeout=10,
                                   params={'output': 'JSON'})
        else:
            if not username:
                return False, "Username is required for Basic auth"
            
            auth_user = f"{username}@{account}"
            response = requests.get(f"{controller_url}/controller/rest/applications",
                                   auth=(auth_user, password), timeout=10,
                                   params={'output': 'JSON'})
        
        if response.status_code == 200:
            apps = response.json()
            app_count = len(apps) if isinstance(apps, list) else 0
            
            return True, f"Successfully authenticated to AppDynamics\nController: {controller_url}\nAccount: {account}\nApplications: {app_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"AppDynamics error: {e}"

