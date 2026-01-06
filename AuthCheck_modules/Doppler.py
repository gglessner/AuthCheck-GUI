# Doppler Secrets Manager Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Doppler (Security)"

form_fields = [
    {"name": "token", "type": "password", "label": "Service Token / Personal Token"},
    {"name": "project", "type": "text", "label": "Project (for Service Token)"},
    {"name": "config", "type": "text", "label": "Config (for Service Token)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Personal token from dashboard.doppler.com/workplace/[team]/tokens. Service token from project settings."},
]


def authenticate(form_data):
    """Attempt to authenticate to Doppler."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    token = form_data.get('token', '').strip()
    project = form_data.get('project', '').strip()
    config = form_data.get('config', '').strip()
    
    if not token:
        return False, "Token is required"
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        # Check if it's a service token or personal token
        if token.startswith('dp.st.'):
            # Service token - access specific project/config
            if not project or not config:
                return False, "Project and Config required for service token"
            
            response = requests.get(
                f"https://api.doppler.com/v3/configs/config/secrets",
                headers=headers,
                params={'project': project, 'config': config},
                timeout=15
            )
            
            if response.status_code == 200:
                secrets = response.json().get('secrets', {})
                secret_count = len(secrets)
                
                return True, f"Successfully authenticated to Doppler\nProject: {project}\nConfig: {config}\nSecrets: {secret_count}"
        else:
            # Personal/CLI token
            response = requests.get("https://api.doppler.com/v3/me",
                                   headers=headers, timeout=15)
            
            if response.status_code == 200:
                user = response.json()
                name = user.get('name', 'unknown')
                email = user.get('email', user.get('slug', 'unknown'))
                
                # Get workplace info
                workplace_resp = requests.get("https://api.doppler.com/v3/workplace",
                                             headers=headers, timeout=10)
                workplace_name = 'unknown'
                if workplace_resp.status_code == 200:
                    workplace_name = workplace_resp.json().get('workplace', {}).get('name', 'unknown')
                
                # Get projects
                projects_resp = requests.get("https://api.doppler.com/v3/projects",
                                            headers=headers, timeout=10)
                project_count = 0
                if projects_resp.status_code == 200:
                    project_count = len(projects_resp.json().get('projects', []))
                
                return True, f"Successfully authenticated to Doppler\nUser: {name} ({email})\nWorkplace: {workplace_name}\nProjects: {project_count}"
        
        if response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Doppler error: {e}"

