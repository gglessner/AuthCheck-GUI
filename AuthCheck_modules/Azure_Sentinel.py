# Microsoft Sentinel (Azure Sentinel) Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Microsoft Sentinel (Security)"

form_fields = [
    {"name": "tenant_id", "type": "text", "label": "Tenant ID"},
    {"name": "client_id", "type": "text", "label": "Client ID"},
    {"name": "client_secret", "type": "password", "label": "Client Secret"},
    {"name": "subscription_id", "type": "text", "label": "Subscription ID"},
    {"name": "resource_group", "type": "text", "label": "Resource Group"},
    {"name": "workspace_name", "type": "text", "label": "Log Analytics Workspace"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "App registration with Microsoft Sentinel Contributor role on the workspace."},
]


def authenticate(form_data):
    """Attempt to authenticate to Microsoft Sentinel."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    tenant_id = form_data.get('tenant_id', '').strip()
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '')
    subscription_id = form_data.get('subscription_id', '').strip()
    resource_group = form_data.get('resource_group', '').strip()
    workspace_name = form_data.get('workspace_name', '').strip()
    
    if not all([tenant_id, client_id, client_secret, subscription_id, resource_group, workspace_name]):
        return False, "All fields are required"
    
    try:
        # Get access token
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://management.azure.com/.default'
        }
        
        token_resp = requests.post(token_url, data=token_data, timeout=15)
        
        if token_resp.status_code == 200:
            access_token = token_resp.json().get('access_token')
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            base_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.OperationalInsights/workspaces/{workspace_name}"
            
            # Get workspace info
            workspace_resp = requests.get(f"{base_url}?api-version=2021-12-01-preview",
                                         headers=headers, timeout=10)
            
            if workspace_resp.status_code == 200:
                workspace = workspace_resp.json()
                
                # Get incident count
                incidents_resp = requests.get(
                    f"{base_url}/providers/Microsoft.SecurityInsights/incidents?api-version=2023-02-01",
                    headers=headers, timeout=10)
                incident_count = 0
                if incidents_resp.status_code == 200:
                    incident_count = len(incidents_resp.json().get('value', []))
                
                # Get data connector count
                connectors_resp = requests.get(
                    f"{base_url}/providers/Microsoft.SecurityInsights/dataConnectors?api-version=2023-02-01",
                    headers=headers, timeout=10)
                connector_count = 0
                if connectors_resp.status_code == 200:
                    connector_count = len(connectors_resp.json().get('value', []))
                
                return True, f"Successfully authenticated to Microsoft Sentinel\nWorkspace: {workspace_name}\nIncidents: {incident_count}\nData Connectors: {connector_count}"
            else:
                return False, f"Workspace access failed: {workspace_resp.status_code}"
        else:
            return False, f"Token request failed: {token_resp.json().get('error_description', 'Unknown error')}"
            
    except Exception as e:
        return False, f"Sentinel error: {e}"

