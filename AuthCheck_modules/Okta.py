# Okta Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Okta (IAM)"

form_fields = [
    {"name": "org_url", "type": "text", "label": "Okta Org URL"},
    {"name": "api_token", "type": "password", "label": "API Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Org URL: xxx.okta.com or xxx.oktapreview.com. API token from Security > API > Tokens."},
]


def authenticate(form_data):
    """Attempt to authenticate to Okta."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    org_url = form_data.get('org_url', '').strip()
    api_token = form_data.get('api_token', '').strip()
    
    if not org_url:
        return False, "Okta Org URL is required"
    if not api_token:
        return False, "API Token is required"
    
    # Normalize URL
    if not org_url.startswith('http'):
        org_url = f"https://{org_url}"
    org_url = org_url.rstrip('/')
    
    try:
        headers = {
            'Authorization': f'SSWS {api_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Get current user (token owner)
        response = requests.get(f"{org_url}/api/v1/users/me", headers=headers, timeout=10)
        
        if response.status_code == 200:
            user = response.json()
            user_email = user.get('profile', {}).get('email', 'unknown')
            user_name = user.get('profile', {}).get('firstName', '') + ' ' + user.get('profile', {}).get('lastName', '')
            user_status = user.get('status', 'unknown')
            
            # Get org info
            org_resp = requests.get(f"{org_url}/api/v1/org", headers=headers, timeout=10)
            org_name = 'unknown'
            if org_resp.status_code == 200:
                org_data = org_resp.json()
                org_name = org_data.get('companyName', 'unknown')
            
            # Get user count
            users_resp = requests.get(f"{org_url}/api/v1/users?limit=1", headers=headers, timeout=10)
            total_users = users_resp.headers.get('x-rate-limit-limit', 'unknown')
            
            return True, f"Successfully authenticated to Okta\nOrg: {org_name}\nUser: {user_name.strip()}\nEmail: {user_email}\nStatus: {user_status}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Okta error: {e}"

