# Azure Active Directory / Entra ID Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Azure AD / Entra ID (IAM)"

form_fields = [
    {"name": "tenant_id", "type": "text", "label": "Tenant ID"},
    {"name": "client_id", "type": "text", "label": "Client ID (App ID)"},
    {"name": "client_secret", "type": "password", "label": "Client Secret"},
    {"name": "username", "type": "text", "label": "Username (for ROPC)"},
    {"name": "password", "type": "password", "label": "Password (for ROPC)"},
    {"name": "auth_type", "type": "combo", "label": "Auth Flow", "options": ["Client Credentials", "Resource Owner Password"], "default": "Client Credentials"},
    {"name": "scope", "type": "text", "label": "Scope", "default": "https://graph.microsoft.com/.default"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Tenant ID: directory GUID or domain.onmicrosoft.com. Client from App Registration."},
]


def authenticate(form_data):
    """Attempt to authenticate to Azure AD / Entra ID."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    tenant_id = form_data.get('tenant_id', '').strip()
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    auth_type = form_data.get('auth_type', 'Client Credentials')
    scope = form_data.get('scope', 'https://graph.microsoft.com/.default').strip()
    
    if not tenant_id:
        return False, "Tenant ID is required"
    if not client_id:
        return False, "Client ID is required"
    
    try:
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        
        if auth_type == "Client Credentials":
            if not client_secret:
                return False, "Client Secret is required for Client Credentials flow"
            
            token_data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'scope': scope,
                'grant_type': 'client_credentials'
            }
        else:  # Resource Owner Password
            if not username or not password:
                return False, "Username and Password required for ROPC flow"
            
            token_data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'scope': scope,
                'grant_type': 'password',
                'username': username,
                'password': password
            }
        
        response = requests.post(token_url, data=token_data, timeout=10)
        
        if response.status_code == 200:
            token_response = response.json()
            access_token = token_response.get('access_token')
            expires_in = token_response.get('expires_in', 0)
            
            # Get tenant info using Graph API
            graph_headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Try to get organization info
            org_resp = requests.get("https://graph.microsoft.com/v1.0/organization",
                                   headers=graph_headers, timeout=10)
            
            org_name = 'unknown'
            if org_resp.status_code == 200:
                org_data = org_resp.json()
                orgs = org_data.get('value', [])
                if orgs:
                    org_name = orgs[0].get('displayName', 'unknown')
            
            if auth_type == "Resource Owner Password":
                # Get user info
                me_resp = requests.get("https://graph.microsoft.com/v1.0/me",
                                      headers=graph_headers, timeout=10)
                user_info = "Service Principal"
                if me_resp.status_code == 200:
                    me_data = me_resp.json()
                    user_info = me_data.get('displayName', me_data.get('userPrincipalName', 'User'))
            else:
                user_info = "Service Principal (App)"
            
            return True, f"Successfully authenticated to Azure AD\nTenant: {org_name}\nIdentity: {user_info}\nToken expires in: {expires_in}s"
        else:
            error_data = response.json()
            error_desc = error_data.get('error_description', error_data.get('error', 'Unknown error'))
            return False, f"Authentication failed: {error_desc}"
            
    except Exception as e:
        return False, f"Azure AD error: {e}"

