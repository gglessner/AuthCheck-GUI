# JetBrains TeamCity Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "JetBrains TeamCity (CI/CD)"

form_fields = [
    {"name": "url", "type": "text", "label": "TeamCity URL"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "token", "type": "password", "label": "Access Token (Alternative)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default port 8111. Token from My Settings & Tools > Access Tokens."},
]


def authenticate(form_data):
    """Attempt to authenticate to TeamCity."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    token = form_data.get('token', '').strip()
    
    if not url:
        return False, "TeamCity URL is required"
    
    if not url.startswith('http'):
        url = f"http://{url}"
    url = url.rstrip('/')
    
    try:
        headers = {'Accept': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
            auth = None
        elif username:
            auth = HTTPBasicAuth(username, password)
        else:
            return False, "Username/Password or Token required"
        
        # Get server info
        response = requests.get(f"{url}/app/rest/server",
                               headers=headers, auth=auth, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('version', 'unknown')
            build_number = data.get('buildNumber', '')
            
            # Get project count
            projects_resp = requests.get(f"{url}/app/rest/projects",
                                        headers=headers, auth=auth, timeout=10)
            project_count = 0
            if projects_resp.status_code == 200:
                project_count = projects_resp.json().get('count', 0)
            
            # Get agent count
            agents_resp = requests.get(f"{url}/app/rest/agents",
                                      headers=headers, auth=auth, timeout=10)
            agent_count = 0
            if agents_resp.status_code == 200:
                agent_count = agents_resp.json().get('count', 0)
            
            # Get build queue
            queue_resp = requests.get(f"{url}/app/rest/buildQueue",
                                     headers=headers, auth=auth, timeout=10)
            queue_count = 0
            if queue_resp.status_code == 200:
                queue_count = queue_resp.json().get('count', 0)
            
            return True, f"Successfully authenticated to TeamCity {version} (build {build_number})\nProjects: {project_count}\nAgents: {agent_count}\nQueued Builds: {queue_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"TeamCity error: {e}"

