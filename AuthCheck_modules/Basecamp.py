# Basecamp Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Basecamp (Collaboration)"

form_fields = [
    {"name": "access_token", "type": "password", "label": "Access Token"},
    {"name": "account_id", "type": "text", "label": "Account ID"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "OAuth access token. Account ID from URL: 3.basecamp.com/ACCOUNT_ID/..."},
]


def authenticate(form_data):
    """Attempt to authenticate to Basecamp."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    access_token = form_data.get('access_token', '').strip()
    account_id = form_data.get('account_id', '').strip()
    
    if not access_token:
        return False, "Access Token is required"
    
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'AuthCheck (contact@example.com)'
        }
        
        # Get authorization info
        auth_resp = requests.get(
            "https://launchpad.37signals.com/authorization.json",
            headers=headers,
            timeout=15
        )
        
        if auth_resp.status_code == 200:
            auth_data = auth_resp.json()
            identity = auth_data.get('identity', {})
            email = identity.get('email_address', 'unknown')
            name = f"{identity.get('first_name', '')} {identity.get('last_name', '')}".strip()
            
            accounts = auth_data.get('accounts', [])
            bc_accounts = [a for a in accounts if a.get('product') == 'bc3']
            
            if account_id:
                # Get projects for specific account
                projects_resp = requests.get(
                    f"https://3.basecampapi.com/{account_id}/projects.json",
                    headers=headers,
                    timeout=10
                )
                project_count = 0
                if projects_resp.status_code == 200:
                    project_count = len(projects_resp.json())
                
                return True, f"Successfully authenticated to Basecamp\nUser: {name} ({email})\nAccount: {account_id}\nProjects: {project_count}"
            else:
                return True, f"Successfully authenticated to Basecamp\nUser: {name} ({email})\nBasecamp 3 Accounts: {len(bc_accounts)}"
        elif auth_resp.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {auth_resp.status_code}: {auth_resp.text[:200]}"
            
    except Exception as e:
        return False, f"Basecamp error: {e}"

