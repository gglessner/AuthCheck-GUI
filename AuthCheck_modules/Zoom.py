# Zoom Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Zoom (Collaboration)"

form_fields = [
    {"name": "account_id", "type": "text", "label": "Account ID"},
    {"name": "client_id", "type": "text", "label": "Client ID"},
    {"name": "client_secret", "type": "password", "label": "Client Secret"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Server-to-Server OAuth app from Zoom App Marketplace. Account ID from app credentials."},
]


def authenticate(form_data):
    """Attempt to authenticate to Zoom API."""
    try:
        import requests
        import base64
    except ImportError:
        return False, "requests package not installed"
    
    account_id = form_data.get('account_id', '').strip()
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '')
    
    if not account_id:
        return False, "Account ID is required"
    if not client_id:
        return False, "Client ID is required"
    if not client_secret:
        return False, "Client Secret is required"
    
    try:
        # Get access token
        auth_string = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        
        token_resp = requests.post(
            "https://zoom.us/oauth/token",
            headers={
                'Authorization': f'Basic {auth_string}',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={
                'grant_type': 'account_credentials',
                'account_id': account_id
            },
            timeout=15
        )
        
        if token_resp.status_code == 200:
            access_token = token_resp.json().get('access_token')
            
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Get account info
            account_resp = requests.get("https://api.zoom.us/v2/accounts/me",
                                       headers=headers, timeout=10)
            account_name = 'unknown'
            if account_resp.status_code == 200:
                account_name = account_resp.json().get('account_name', 'unknown')
            
            # Get user count
            users_resp = requests.get("https://api.zoom.us/v2/users?page_size=1",
                                     headers=headers, timeout=10)
            user_count = 0
            if users_resp.status_code == 200:
                user_count = users_resp.json().get('total_records', 0)
            
            return True, f"Successfully authenticated to Zoom\nAccount: {account_name}\nUsers: {user_count}"
        elif token_resp.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            try:
                error_data = token_resp.json()
                error_msg = error_data.get('reason', error_data.get('error', token_resp.text[:200]))
            except:
                error_msg = token_resp.text[:200]
            return False, f"Authentication failed: {error_msg}"
            
    except Exception as e:
        return False, f"Zoom error: {e}"

