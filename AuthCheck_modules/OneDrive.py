# OneDrive Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "OneDrive (Collaboration)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID"},
    {"name": "client_secret", "type": "password", "label": "Client Secret"},
    {"name": "tenant_id", "type": "text", "label": "Tenant ID"},
    {"name": "access_token", "type": "password", "label": "Access Token (Alternative)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "App registration from Azure AD. Requires Files.Read.All permission."},
]


def authenticate(form_data):
    """Attempt to authenticate to OneDrive."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '').strip()
    tenant_id = form_data.get('tenant_id', '').strip()
    access_token = form_data.get('access_token', '').strip()
    
    try:
        if access_token:
            token = access_token
        else:
            if not client_id:
                return False, "Client ID is required"
            if not client_secret:
                return False, "Client Secret is required"
            if not tenant_id:
                return False, "Tenant ID is required"
            
            # Get access token
            token_resp = requests.post(
                f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
                data={
                    'grant_type': 'client_credentials',
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'scope': 'https://graph.microsoft.com/.default'
                },
                timeout=15
            )
            
            if token_resp.status_code != 200:
                return False, f"Token error: {token_resp.json().get('error_description', 'Unknown error')}"
            
            token = token_resp.json().get('access_token')
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get drives (for org)
        drives_resp = requests.get(
            "https://graph.microsoft.com/v1.0/drives",
            headers=headers,
            timeout=15
        )
        
        if drives_resp.status_code == 200:
            drives = drives_resp.json().get('value', [])
            drive_count = len(drives)
            
            return True, f"Successfully authenticated to OneDrive/Microsoft Graph\nDrives: {drive_count}"
        elif drives_resp.status_code == 401:
            return False, "Authentication failed: Invalid or expired token"
        else:
            return False, f"HTTP {drives_resp.status_code}: {drives_resp.text[:200]}"
            
    except Exception as e:
        return False, f"OneDrive error: {e}"

