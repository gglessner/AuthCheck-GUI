# Genesys Cloud Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Genesys Cloud (PBX)"

form_fields = [
    {"name": "region", "type": "combo", "label": "Region", "options": ["mypurecloud.com", "mypurecloud.ie", "mypurecloud.de", "mypurecloud.com.au", "mypurecloud.jp", "usw2.pure.cloud", "cac1.pure.cloud", "euw2.pure.cloud", "apne2.pure.cloud", "aps1.pure.cloud", "sae1.pure.cloud"], "default": "mypurecloud.com"},
    {"name": "client_id", "type": "text", "label": "Client ID"},
    {"name": "client_secret", "type": "password", "label": "Client Secret"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "OAuth credentials from Admin > Integrations > OAuth. Client Credentials grant."},
]


def authenticate(form_data):
    """Attempt to authenticate to Genesys Cloud."""
    try:
        import requests
        import base64
    except ImportError:
        return False, "requests package not installed"
    
    region = form_data.get('region', 'mypurecloud.com')
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '').strip()
    
    if not client_id:
        return False, "Client ID is required"
    if not client_secret:
        return False, "Client Secret is required"
    
    try:
        # Get OAuth token
        auth_string = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        
        token_url = f"https://login.{region}/oauth/token"
        
        response = requests.post(
            token_url,
            headers={
                'Authorization': f'Basic {auth_string}',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={'grant_type': 'client_credentials'},
            timeout=15
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            
            # Get organization info
            api_url = f"https://api.{region}/api/v2/organizations/me"
            org_resp = requests.get(
                api_url,
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10
            )
            
            org_name = 'unknown'
            if org_resp.status_code == 200:
                org_data = org_resp.json()
                org_name = org_data.get('name', 'unknown')
            
            # Get user count
            users_resp = requests.get(
                f"https://api.{region}/api/v2/users?pageSize=1",
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10
            )
            user_count = 0
            if users_resp.status_code == 200:
                user_count = users_resp.json().get('total', 0)
            
            return True, f"Successfully authenticated to Genesys Cloud\nRegion: {region}\nOrganization: {org_name}\nUsers: {user_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            try:
                error = response.json().get('description', response.text[:200])
            except:
                error = response.text[:200]
            return False, f"HTTP {response.status_code}: {error}"
            
    except Exception as e:
        return False, f"Genesys Cloud error: {e}"

