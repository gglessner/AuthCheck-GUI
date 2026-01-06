# MuleSoft Anypoint Platform Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "MuleSoft Anypoint (Middleware)"

form_fields = [
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "client_id", "type": "text", "label": "Connected App Client ID (Alternative)"},
    {"name": "client_secret", "type": "password", "label": "Connected App Client Secret"},
    {"name": "org_id", "type": "text", "label": "Organization ID (Optional)"},
    {"name": "region", "type": "combo", "label": "Region", "options": ["US", "EU"], "default": "US"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Username/password or Connected App credentials. From anypoint.mulesoft.com Access Management."},
]


def authenticate(form_data):
    """Attempt to authenticate to MuleSoft Anypoint Platform."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '')
    org_id = form_data.get('org_id', '').strip()
    region = form_data.get('region', 'US')
    
    try:
        # Regional base URLs
        if region == "EU":
            base_url = "https://eu1.anypoint.mulesoft.com"
        else:
            base_url = "https://anypoint.mulesoft.com"
        
        headers = {'Content-Type': 'application/json'}
        
        if client_id and client_secret:
            # Connected App authentication
            auth_data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'client_credentials'
            }
            response = requests.post(f"{base_url}/accounts/api/v2/oauth2/token",
                                    json=auth_data, headers=headers, timeout=15)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                auth_headers = {
                    'Authorization': f"Bearer {access_token}",
                    'Content-Type': 'application/json'
                }
            else:
                return False, f"Connected App auth failed: {response.text[:200]}"
        else:
            if not username or not password:
                return False, "Username/Password or Connected App credentials required"
            
            # Username/password authentication
            auth_data = {
                'username': username,
                'password': password
            }
            response = requests.post(f"{base_url}/accounts/login",
                                    json=auth_data, headers=headers, timeout=15)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                auth_headers = {
                    'Authorization': f"Bearer {access_token}",
                    'Content-Type': 'application/json'
                }
            else:
                return False, f"Login failed: {response.text[:200]}"
        
        # Get user/organization info
        me_resp = requests.get(f"{base_url}/accounts/api/me",
                              headers=auth_headers, timeout=10)
        
        if me_resp.status_code == 200:
            me_data = me_resp.json()
            user_data = me_data.get('user', {})
            user_name = f"{user_data.get('firstName', '')} {user_data.get('lastName', '')}".strip() or username
            
            org_data = me_data.get('user', {}).get('organization', {})
            org_name = org_data.get('name', 'unknown')
            
            # Get environment count
            env_count = len(me_data.get('user', {}).get('memberOfOrganizations', []))
            
            return True, f"Successfully authenticated to MuleSoft Anypoint\nRegion: {region}\nOrganization: {org_name}\nUser: {user_name}\nOrganizations: {env_count}"
        else:
            return False, f"Failed to get user info: {me_resp.text[:200]}"
            
    except Exception as e:
        return False, f"MuleSoft error: {e}"

