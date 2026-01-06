# SailPoint IdentityNow Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "SailPoint IdentityNow (IAM)"

form_fields = [
    {"name": "tenant", "type": "text", "label": "Tenant Name"},
    {"name": "client_id", "type": "text", "label": "Client ID"},
    {"name": "client_secret", "type": "password", "label": "Client Secret"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Tenant: xxx.identitynow.com. API credentials from Admin > Global > Security Settings > API Management."},
]


def authenticate(form_data):
    """Attempt to authenticate to SailPoint IdentityNow."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    tenant = form_data.get('tenant', '').strip()
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '')
    
    if not tenant:
        return False, "Tenant Name is required"
    if not client_id:
        return False, "Client ID is required"
    if not client_secret:
        return False, "Client Secret is required"
    
    # Normalize tenant
    if not tenant.endswith('.identitynow.com') and not tenant.endswith('.api.identitynow.com'):
        tenant = f"{tenant}.api.identitynow.com"
    if not tenant.startswith('http'):
        tenant = f"https://{tenant}"
    tenant = tenant.rstrip('/')
    
    try:
        # Get access token
        token_url = f"{tenant}/oauth/token"
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        
        token_resp = requests.post(token_url, data=token_data, timeout=15)
        
        if token_resp.status_code == 200:
            access_token = token_resp.json().get('access_token')
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get tenant info
            # Note: API paths may vary by version
            info_resp = requests.get(f"{tenant}/beta/tenant",
                                    headers=headers, timeout=10)
            tenant_name = 'unknown'
            if info_resp.status_code == 200:
                tenant_name = info_resp.json().get('name', 'unknown')
            
            # Get identity count
            identity_resp = requests.get(f"{tenant}/v3/search/identities",
                                        headers=headers,
                                        json={'query': {'query': '*'}, 'indices': ['identities']},
                                        timeout=15)
            identity_count = 0
            if identity_resp.status_code == 200:
                identity_count = identity_resp.json().get('count', 0)
            
            # Get source count
            sources_resp = requests.get(f"{tenant}/v3/sources",
                                       headers=headers, timeout=10)
            source_count = 0
            if sources_resp.status_code == 200:
                source_count = len(sources_resp.json())
            
            return True, f"Successfully authenticated to SailPoint IdentityNow\nTenant: {tenant_name}\nIdentities: {identity_count}\nSources: {source_count}"
        elif token_resp.status_code == 401:
            return False, "Authentication failed: Invalid client credentials"
        else:
            try:
                error_data = token_resp.json()
                error_msg = error_data.get('error_description', error_data.get('error', token_resp.text[:200]))
            except:
                error_msg = token_resp.text[:200]
            return False, f"Authentication failed: {error_msg}"
            
    except Exception as e:
        return False, f"SailPoint error: {e}"

