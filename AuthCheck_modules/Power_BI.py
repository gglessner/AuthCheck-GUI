# Microsoft Power BI Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Microsoft Power BI (Analytics)"

form_fields = [
    {"name": "tenant_id", "type": "text", "label": "Tenant ID"},
    {"name": "client_id", "type": "text", "label": "Client ID (App ID)"},
    {"name": "client_secret", "type": "password", "label": "Client Secret"},
    {"name": "username", "type": "text", "label": "Username (Master User)"},
    {"name": "password", "type": "password", "label": "Password (Master User)"},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["Service Principal", "Master User"], "default": "Service Principal"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "App registration in Azure AD with Power BI permissions. Service Principal needs Power BI Admin enablement."},
]


def authenticate(form_data):
    """Attempt to authenticate to Microsoft Power BI."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    tenant_id = form_data.get('tenant_id', '').strip()
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    auth_type = form_data.get('auth_type', 'Service Principal')
    
    if not tenant_id:
        return False, "Tenant ID is required"
    if not client_id:
        return False, "Client ID is required"
    
    try:
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        
        if auth_type == "Service Principal":
            if not client_secret:
                return False, "Client Secret required for Service Principal"
            
            token_data = {
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret,
                'scope': 'https://analysis.windows.net/powerbi/api/.default'
            }
        else:
            if not username or not password:
                return False, "Username and Password required for Master User"
            
            token_data = {
                'grant_type': 'password',
                'client_id': client_id,
                'client_secret': client_secret,
                'scope': 'https://analysis.windows.net/powerbi/api/.default',
                'username': username,
                'password': password
            }
        
        token_resp = requests.post(token_url, data=token_data, timeout=15)
        
        if token_resp.status_code == 200:
            access_token = token_resp.json().get('access_token')
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get groups (workspaces)
            groups_resp = requests.get("https://api.powerbi.com/v1.0/myorg/groups",
                                       headers=headers, timeout=10)
            workspace_count = 0
            if groups_resp.status_code == 200:
                workspace_count = len(groups_resp.json().get('value', []))
            
            # Get datasets
            datasets_resp = requests.get("https://api.powerbi.com/v1.0/myorg/datasets",
                                        headers=headers, timeout=10)
            dataset_count = 0
            if datasets_resp.status_code == 200:
                dataset_count = len(datasets_resp.json().get('value', []))
            
            # Get reports
            reports_resp = requests.get("https://api.powerbi.com/v1.0/myorg/reports",
                                       headers=headers, timeout=10)
            report_count = 0
            if reports_resp.status_code == 200:
                report_count = len(reports_resp.json().get('value', []))
            
            return True, f"Successfully authenticated to Power BI\nAuth Type: {auth_type}\nWorkspaces: {workspace_count}\nDatasets: {dataset_count}\nReports: {report_count}"
        else:
            error_data = token_resp.json()
            error_msg = error_data.get('error_description', error_data.get('error', 'Unknown error'))
            return False, f"Authentication failed: {error_msg}"
            
    except Exception as e:
        return False, f"Power BI error: {e}"

