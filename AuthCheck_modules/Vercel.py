# Vercel Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Vercel (Cloud)"

form_fields = [
    {"name": "token", "type": "password", "label": "Access Token"},
    {"name": "team_id", "type": "text", "label": "Team ID (Optional)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Access token from vercel.com/account/tokens. Team ID from team settings."},
]


def authenticate(form_data):
    """Attempt to authenticate to Vercel."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    token = form_data.get('token', '').strip()
    team_id = form_data.get('team_id', '').strip()
    
    if not token:
        return False, "Access Token is required"
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        params = {}
        if team_id:
            params['teamId'] = team_id
        
        # Get user info
        response = requests.get("https://api.vercel.com/v2/user",
                               headers=headers, timeout=15)
        
        if response.status_code == 200:
            user = response.json().get('user', {})
            username = user.get('username', 'unknown')
            email = user.get('email', 'unknown')
            
            # Get projects
            projects_resp = requests.get("https://api.vercel.com/v9/projects",
                                        headers=headers, params=params, timeout=10)
            project_count = 0
            project_names = []
            if projects_resp.status_code == 200:
                projects = projects_resp.json().get('projects', [])
                project_count = len(projects)
                project_names = [p['name'] for p in projects[:3]]
            
            # Get deployments
            deployments_resp = requests.get("https://api.vercel.com/v6/deployments?limit=10",
                                           headers=headers, params=params, timeout=10)
            deployment_count = 0
            if deployments_resp.status_code == 200:
                deployment_count = len(deployments_resp.json().get('deployments', []))
            
            team_info = f"\nTeam ID: {team_id}" if team_id else ""
            return True, f"Successfully authenticated to Vercel\nUser: {username} ({email}){team_info}\nProjects: {project_count}\nRecent Deployments: {deployment_count}\nSample Projects: {', '.join(project_names) if project_names else 'none'}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        elif response.status_code == 403:
            return False, "Authentication failed: Token lacks required scopes"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Vercel error: {e}"

