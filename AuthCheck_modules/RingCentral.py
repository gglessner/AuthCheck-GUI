# RingCentral Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "RingCentral (PBX)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID"},
    {"name": "client_secret", "type": "password", "label": "Client Secret"},
    {"name": "jwt_token", "type": "password", "label": "JWT Token"},
    {"name": "server_url", "type": "combo", "label": "Server", "options": ["https://platform.ringcentral.com", "https://platform.devtest.ringcentral.com"], "default": "https://platform.ringcentral.com"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "OAuth credentials from Developer Portal. JWT for server-to-server auth."},
]


def authenticate(form_data):
    """Attempt to authenticate to RingCentral."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '').strip()
    jwt_token = form_data.get('jwt_token', '').strip()
    server_url = form_data.get('server_url', 'https://platform.ringcentral.com')
    
    if not client_id:
        return False, "Client ID is required"
    if not jwt_token:
        return False, "JWT Token is required"
    
    try:
        # Get OAuth token using JWT
        import base64
        
        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        
        token_resp = requests.post(
            f"{server_url}/restapi/oauth/token",
            headers={
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={
                'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'assertion': jwt_token
            },
            timeout=15
        )
        
        if token_resp.status_code == 200:
            token_data = token_resp.json()
            access_token = token_data.get('access_token')
            
            # Get account info
            headers = {'Authorization': f'Bearer {access_token}'}
            
            account_resp = requests.get(
                f"{server_url}/restapi/v1.0/account/~",
                headers=headers,
                timeout=10
            )
            
            if account_resp.status_code == 200:
                account = account_resp.json()
                account_id = account.get('id', 'unknown')
                company = account.get('mainNumber', 'unknown')
                
                # Get extensions count
                ext_resp = requests.get(
                    f"{server_url}/restapi/v1.0/account/~/extension?perPage=1",
                    headers=headers,
                    timeout=10
                )
                ext_count = 0
                if ext_resp.status_code == 200:
                    ext_count = ext_resp.json().get('paging', {}).get('totalRecords', 0)
                
                return True, f"Successfully authenticated to RingCentral\nAccount ID: {account_id}\nMain Number: {company}\nExtensions: {ext_count}"
            
            return True, f"Successfully authenticated to RingCentral\nToken obtained"
        elif token_resp.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            try:
                error = token_resp.json().get('error_description', token_resp.text[:200])
            except:
                error = token_resp.text[:200]
            return False, f"HTTP {token_resp.status_code}: {error}"
            
    except Exception as e:
        return False, f"RingCentral error: {e}"

