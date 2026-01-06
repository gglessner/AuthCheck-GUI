# Wrike Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Wrike (Collaboration)"

form_fields = [
    {"name": "access_token", "type": "password", "label": "Access Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Permanent access token from Settings > Apps & Integrations > API."},
]


def authenticate(form_data):
    """Attempt to authenticate to Wrike."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    access_token = form_data.get('access_token', '').strip()
    
    if not access_token:
        return False, "Access Token is required"
    
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Get account info
        response = requests.get(
            "https://www.wrike.com/api/v4/account",
            headers=headers, timeout=15
        )
        
        if response.status_code == 200:
            data = response.json().get('data', [{}])[0]
            account_name = data.get('name', 'unknown')
            
            # Get user contacts
            contacts_resp = requests.get(
                "https://www.wrike.com/api/v4/contacts",
                headers=headers, timeout=10
            )
            user_count = 0
            if contacts_resp.status_code == 200:
                user_count = len(contacts_resp.json().get('data', []))
            
            # Get folders
            folders_resp = requests.get(
                "https://www.wrike.com/api/v4/folders",
                headers=headers, timeout=10
            )
            folder_count = 0
            if folders_resp.status_code == 200:
                folder_count = len(folders_resp.json().get('data', []))
            
            return True, f"Successfully authenticated to Wrike\nAccount: {account_name}\nUsers: {user_count}\nFolders: {folder_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Wrike error: {e}"

