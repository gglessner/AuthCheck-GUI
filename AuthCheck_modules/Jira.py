# Atlassian Jira Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Atlassian Jira (Collaboration)"

form_fields = [
    {"name": "url", "type": "text", "label": "Jira URL"},
    {"name": "email", "type": "text", "label": "Email (Cloud) / Username (Server)"},
    {"name": "api_token", "type": "password", "label": "API Token (Cloud) / Password (Server)"},
    {"name": "deployment", "type": "combo", "label": "Deployment Type", "options": ["Cloud", "Server/Data Center"], "default": "Cloud"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Cloud: xxx.atlassian.net, API token from id.atlassian.com. Server: hostname:8080, use password."},
]


def authenticate(form_data):
    """Attempt to authenticate to Atlassian Jira."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', '').strip()
    email = form_data.get('email', '').strip()
    api_token = form_data.get('api_token', '')
    deployment = form_data.get('deployment', 'Cloud')
    
    if not url:
        return False, "Jira URL is required"
    if not email:
        return False, "Email/Username is required"
    if not api_token:
        return False, "API Token/Password is required"
    
    if not url.startswith('http'):
        url = f"https://{url}"
    url = url.rstrip('/')
    
    try:
        auth = HTTPBasicAuth(email, api_token)
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Get current user
        response = requests.get(f"{url}/rest/api/2/myself",
                               auth=auth, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            display_name = user_data.get('displayName', 'unknown')
            account_id = user_data.get('accountId', user_data.get('name', 'unknown'))
            
            # Get server info
            server_resp = requests.get(f"{url}/rest/api/2/serverInfo",
                                       auth=auth, headers=headers, timeout=10)
            version = 'unknown'
            server_title = 'Jira'
            if server_resp.status_code == 200:
                server_data = server_resp.json()
                version = server_data.get('version', 'unknown')
                server_title = server_data.get('serverTitle', 'Jira')
            
            # Get project count
            projects_resp = requests.get(f"{url}/rest/api/2/project",
                                        auth=auth, headers=headers, timeout=10)
            project_count = 0
            if projects_resp.status_code == 200:
                project_count = len(projects_resp.json())
            
            return True, f"Successfully authenticated to {server_title}\nVersion: {version}\nUser: {display_name}\nProjects: {project_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Jira error: {e}"

