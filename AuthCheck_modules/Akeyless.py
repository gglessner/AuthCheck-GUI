# Akeyless Vault Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Akeyless Vault (Security)"

form_fields = [
    {"name": "api_url", "type": "text", "label": "API URL", "default": "https://api.akeyless.io"},
    {"name": "access_id", "type": "text", "label": "Access ID"},
    {"name": "access_key", "type": "password", "label": "Access Key"},
    {"name": "api_key", "type": "password", "label": "API Key (Alternative)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "SaaS secrets manager. Access ID/Key from Console > Access Roles."},
]


def authenticate(form_data):
    """Attempt to authenticate to Akeyless Vault."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    api_url = form_data.get('api_url', 'https://api.akeyless.io').strip()
    access_id = form_data.get('access_id', '').strip()
    access_key = form_data.get('access_key', '').strip()
    api_key = form_data.get('api_key', '').strip()
    
    if not api_url:
        api_url = "https://api.akeyless.io"
    
    api_url = api_url.rstrip('/')
    
    try:
        if api_key:
            # API key authentication
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # List secrets to verify
            response = requests.post(
                f"{api_url}/list-items",
                headers=headers,
                json={},
                timeout=15
            )
        elif access_id and access_key:
            # Access ID/Key authentication
            auth_resp = requests.post(
                f"{api_url}/auth",
                json={
                    'access-id': access_id,
                    'access-key': access_key,
                    'access-type': 'access_key'
                },
                timeout=15
            )
            
            if auth_resp.status_code == 200:
                token = auth_resp.json().get('token')
                
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                # Get account info
                account_resp = requests.post(
                    f"{api_url}/get-account-settings",
                    headers=headers,
                    json={},
                    timeout=10
                )
                
                account_name = 'unknown'
                if account_resp.status_code == 200:
                    account = account_resp.json()
                    account_name = account.get('account_name', 'unknown')
                
                # List items
                items_resp = requests.post(
                    f"{api_url}/list-items",
                    headers=headers,
                    json={},
                    timeout=10
                )
                
                item_count = 0
                if items_resp.status_code == 200:
                    items = items_resp.json().get('items', [])
                    item_count = len(items)
                
                return True, f"Successfully authenticated to Akeyless Vault\nAPI: {api_url}\nAccount: {account_name}\nAccess ID: {access_id}\nItems: {item_count}"
            elif auth_resp.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            else:
                try:
                    error = auth_resp.json().get('message', auth_resp.text[:200])
                except:
                    error = auth_resp.text[:200]
                return False, f"HTTP {auth_resp.status_code}: {error}"
        else:
            return False, "Access ID/Key or API Key required"
        
        return False, "Could not authenticate"
            
    except Exception as e:
        return False, f"Akeyless error: {e}"

