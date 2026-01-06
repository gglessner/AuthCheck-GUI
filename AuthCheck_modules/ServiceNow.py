# ServiceNow Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "ServiceNow (ITSM)"

form_fields = [
    {"name": "instance", "type": "text", "label": "Instance Name"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "client_id", "type": "text", "label": "Client ID (OAuth)"},
    {"name": "client_secret", "type": "password", "label": "Client Secret (OAuth)"},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["Basic", "OAuth"], "default": "Basic"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Instance: xxx.service-now.com. admin / (set during provisioning). OAuth via System OAuth > Application Registry."},
]


def authenticate(form_data):
    """Attempt to authenticate to ServiceNow."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    instance = form_data.get('instance', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '')
    auth_type = form_data.get('auth_type', 'Basic')
    
    if not instance:
        return False, "Instance Name is required"
    
    # Normalize instance URL
    if not instance.endswith('.service-now.com'):
        instance = f"{instance}.service-now.com"
    base_url = f"https://{instance}"
    
    try:
        if auth_type == "OAuth":
            if not client_id or not client_secret:
                return False, "Client ID and Client Secret required for OAuth"
            
            token_url = f"{base_url}/oauth_token.do"
            token_data = {
                'grant_type': 'password',
                'client_id': client_id,
                'client_secret': client_secret,
                'username': username,
                'password': password
            }
            token_resp = requests.post(token_url, data=token_data, timeout=10)
            
            if token_resp.status_code != 200:
                return False, f"OAuth token request failed: {token_resp.status_code}"
            
            access_token = token_resp.json().get('access_token')
            headers = {'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}
            
            response = requests.get(f"{base_url}/api/now/table/sys_user?sysparm_query=user_name={username}&sysparm_limit=1",
                                   headers=headers, timeout=10)
        else:
            if not username:
                return False, "Username is required"
            
            headers = {'Accept': 'application/json'}
            response = requests.get(f"{base_url}/api/now/table/sys_user?sysparm_query=user_name={username}&sysparm_limit=1",
                                   auth=(username, password), headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            users = data.get('result', [])
            
            if users:
                user = users[0]
                user_name = user.get('name', username)
                user_email = user.get('email', 'unknown')
                
                # Get instance info
                if auth_type == "OAuth":
                    info_resp = requests.get(f"{base_url}/api/now/table/sys_properties?sysparm_query=name=instance_name&sysparm_limit=1",
                                            headers=headers, timeout=10)
                else:
                    info_resp = requests.get(f"{base_url}/api/now/table/sys_properties?sysparm_query=name=instance_name&sysparm_limit=1",
                                            auth=(username, password), headers=headers, timeout=10)
                
                return True, f"Successfully authenticated to ServiceNow\nInstance: {instance}\nUser: {user_name}\nEmail: {user_email}"
            else:
                return True, f"Successfully authenticated to ServiceNow\nInstance: {instance}\nUser: {username}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"ServiceNow error: {e}"

