# Databricks Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Databricks (Cloud)"

form_fields = [
    {"name": "host", "type": "text", "label": "Workspace URL"},
    {"name": "token", "type": "password", "label": "Personal Access Token"},
    {"name": "auth_type", "type": "combo", "label": "Authentication", "options": ["PAT (Token)", "Azure AD", "OAuth"], "default": "PAT (Token)"},
    {"name": "cluster_id", "type": "text", "label": "Cluster ID (Optional)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Workspace URL: adb-xxx.azuredatabricks.net or xxx.cloud.databricks.com"},
]


def authenticate(form_data):
    """Attempt to authenticate to Databricks."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    token = form_data.get('token', '').strip()
    auth_type = form_data.get('auth_type', 'PAT (Token)')
    cluster_id = form_data.get('cluster_id', '').strip()
    
    if not host:
        return False, "Workspace URL is required"
    if auth_type == "PAT (Token)" and not token:
        return False, "Personal Access Token is required"
    
    # Normalize host
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Get current user
        response = requests.get(f"{host}/api/2.0/preview/scim/v2/Me", headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            username = user_data.get('userName', 'unknown')
            display_name = user_data.get('displayName', username)
            
            # Get clusters
            clusters_resp = requests.get(f"{host}/api/2.0/clusters/list", headers=headers, timeout=10)
            cluster_count = 0
            if clusters_resp.status_code == 200:
                clusters = clusters_resp.json().get('clusters', [])
                cluster_count = len(clusters)
            
            # Get workspace status
            workspace_resp = requests.get(f"{host}/api/2.0/workspace/get-status", 
                                         headers=headers, params={'path': '/'}, timeout=10)
            
            return True, f"Successfully authenticated to Databricks\nUser: {display_name} ({username})\nClusters: {cluster_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Databricks error: {e}"

