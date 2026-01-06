# Salesforce Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Salesforce (CRM)"

form_fields = [
    {"name": "instance_url", "type": "text", "label": "Instance URL"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "security_token", "type": "password", "label": "Security Token"},
    {"name": "client_id", "type": "text", "label": "Consumer Key (OAuth)"},
    {"name": "client_secret", "type": "password", "label": "Consumer Secret (OAuth)"},
    {"name": "sandbox", "type": "checkbox", "label": "Sandbox Environment"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Instance URL: xxx.salesforce.com. Security token from User Settings > Reset Security Token."},
]


def authenticate(form_data):
    """Attempt to authenticate to Salesforce."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    instance_url = form_data.get('instance_url', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    security_token = form_data.get('security_token', '')
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '')
    sandbox = form_data.get('sandbox', False)
    
    if not username:
        return False, "Username is required"
    if not password:
        return False, "Password is required"
    
    try:
        # Login endpoint
        if sandbox:
            login_url = "https://test.salesforce.com/services/oauth2/token"
        else:
            login_url = "https://login.salesforce.com/services/oauth2/token"
        
        if client_id and client_secret:
            # OAuth 2.0 flow
            auth_data = {
                'grant_type': 'password',
                'client_id': client_id,
                'client_secret': client_secret,
                'username': username,
                'password': password + security_token
            }
        else:
            # Use SOAP login
            # For simplicity, we'll use the OAuth password flow with default connected app
            return False, "Consumer Key and Consumer Secret are required for API access"
        
        response = requests.post(login_url, data=auth_data, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            instance_url = data.get('instance_url')
            
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Get org info
            org_resp = requests.get(f"{instance_url}/services/data/v58.0/sobjects/Organization",
                                   headers=headers, timeout=10)
            org_name = 'unknown'
            if org_resp.status_code == 200:
                org_name = org_resp.json().get('Name', 'unknown')
            
            # Get user info
            user_resp = requests.get(f"{instance_url}/services/oauth2/userinfo",
                                    headers=headers, timeout=10)
            user_name = username
            if user_resp.status_code == 200:
                user_name = user_resp.json().get('name', username)
            
            # Get limits
            limits_resp = requests.get(f"{instance_url}/services/data/v58.0/limits",
                                      headers=headers, timeout=10)
            api_requests = 'unknown'
            if limits_resp.status_code == 200:
                limits = limits_resp.json()
                daily_api = limits.get('DailyApiRequests', {})
                api_requests = f"{daily_api.get('Remaining', '?')}/{daily_api.get('Max', '?')}"
            
            return True, f"Successfully authenticated to Salesforce\nOrg: {org_name}\nUser: {user_name}\nAPI Requests Remaining: {api_requests}"
        elif response.status_code == 400:
            error_data = response.json()
            return False, f"Authentication failed: {error_data.get('error_description', 'Unknown error')}"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Salesforce error: {e}"

