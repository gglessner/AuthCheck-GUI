# Smartsheet Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Smartsheet (Collaboration)"

form_fields = [
    {"name": "access_token", "type": "password", "label": "Access Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Access token from Account > Personal Settings > API Access."},
]


def authenticate(form_data):
    """Attempt to authenticate to Smartsheet."""
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
        
        # Get current user
        response = requests.get(
            "https://api.smartsheet.com/2.0/users/me",
            headers=headers, timeout=15
        )
        
        if response.status_code == 200:
            user = response.json()
            email = user.get('email', 'unknown')
            name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
            admin = user.get('admin', False)
            
            # Get sheets
            sheets_resp = requests.get(
                "https://api.smartsheet.com/2.0/sheets",
                headers=headers, timeout=10
            )
            sheet_count = 0
            if sheets_resp.status_code == 200:
                sheet_count = sheets_resp.json().get('totalCount', 0)
            
            # Get workspaces
            ws_resp = requests.get(
                "https://api.smartsheet.com/2.0/workspaces",
                headers=headers, timeout=10
            )
            ws_count = 0
            if ws_resp.status_code == 200:
                ws_count = len(ws_resp.json().get('data', []))
            
            return True, f"Successfully authenticated to Smartsheet\nUser: {name} ({email})\nAdmin: {admin}\nSheets: {sheet_count}\nWorkspaces: {ws_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Smartsheet error: {e}"

