# Microsoft Teams Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Microsoft Teams (Collaboration)"

form_fields = [
    {"name": "tenant_id", "type": "text", "label": "Tenant ID"},
    {"name": "client_id", "type": "text", "label": "Client ID (App ID)"},
    {"name": "client_secret", "type": "password", "label": "Client Secret"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "App registration in Azure AD with Teams permissions. Uses Microsoft Graph API."},
]


def authenticate(form_data):
    """Attempt to authenticate to Microsoft Teams via Graph API."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    tenant_id = form_data.get('tenant_id', '').strip()
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '')
    
    if not tenant_id:
        return False, "Tenant ID is required"
    if not client_id:
        return False, "Client ID is required"
    if not client_secret:
        return False, "Client Secret is required"
    
    try:
        # Get access token
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        token_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://graph.microsoft.com/.default',
            'grant_type': 'client_credentials'
        }
        
        token_resp = requests.post(token_url, data=token_data, timeout=10)
        
        if token_resp.status_code == 200:
            access_token = token_resp.json().get('access_token')
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get organization info
            org_resp = requests.get("https://graph.microsoft.com/v1.0/organization",
                                   headers=headers, timeout=10)
            org_name = 'unknown'
            if org_resp.status_code == 200:
                orgs = org_resp.json().get('value', [])
                if orgs:
                    org_name = orgs[0].get('displayName', 'unknown')
            
            # Try to list teams (requires Team.ReadBasic.All)
            teams_resp = requests.get("https://graph.microsoft.com/v1.0/groups?$filter=resourceProvisioningOptions/Any(x:x eq 'Team')",
                                     headers=headers, timeout=10)
            team_count = 0
            if teams_resp.status_code == 200:
                team_count = len(teams_resp.json().get('value', []))
            
            # Get user count
            users_resp = requests.get("https://graph.microsoft.com/v1.0/users?$top=1&$count=true",
                                     headers=headers, timeout=10)
            user_info = ""
            if users_resp.status_code == 200:
                total = users_resp.headers.get('x-ms-total-count')
                if total:
                    user_info = f"\nUsers: {total}"
            
            return True, f"Successfully authenticated to Microsoft Teams\nOrganization: {org_name}\nTeams: {team_count}{user_info}"
        else:
            error_data = token_resp.json()
            error_desc = error_data.get('error_description', error_data.get('error', 'Unknown error'))
            return False, f"Authentication failed: {error_desc}"
            
    except Exception as e:
        return False, f"Microsoft Teams error: {e}"

