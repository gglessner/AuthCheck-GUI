# Asana Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Asana (Collaboration)"

form_fields = [
    {"name": "access_token", "type": "password", "label": "Personal Access Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "PAT from My Settings > Apps > Developer Apps > Personal Access Tokens."},
]


def authenticate(form_data):
    """Attempt to authenticate to Asana."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    access_token = form_data.get('access_token', '').strip()
    
    if not access_token:
        return False, "Personal Access Token is required"
    
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        # Get current user
        response = requests.get("https://app.asana.com/api/1.0/users/me",
                               headers=headers, timeout=15)
        
        if response.status_code == 200:
            user = response.json().get('data', {})
            user_name = user.get('name', 'unknown')
            email = user.get('email', 'unknown')
            
            # Get workspaces
            workspaces = user.get('workspaces', [])
            workspace_names = [w['name'] for w in workspaces[:3]]
            
            # Get project count in first workspace
            project_count = 0
            if workspaces:
                projects_resp = requests.get(
                    f"https://app.asana.com/api/1.0/workspaces/{workspaces[0]['gid']}/projects",
                    headers=headers, timeout=10)
                if projects_resp.status_code == 200:
                    project_count = len(projects_resp.json().get('data', []))
            
            return True, f"Successfully authenticated to Asana\nUser: {user_name} ({email})\nWorkspaces: {len(workspaces)}\nProjects (first workspace): {project_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Asana error: {e}"

