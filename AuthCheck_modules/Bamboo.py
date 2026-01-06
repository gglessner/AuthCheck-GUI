# Atlassian Bamboo Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Atlassian Bamboo (CI/CD)"

form_fields = [
    {"name": "url", "type": "text", "label": "Bamboo URL"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password/Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default port 8085. Use API token instead of password for better security."},
]


def authenticate(form_data):
    """Attempt to authenticate to Atlassian Bamboo."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    if not url:
        return False, "Bamboo URL is required"
    if not username:
        return False, "Username is required"
    
    if not url.startswith('http'):
        url = f"http://{url}"
    url = url.rstrip('/')
    
    try:
        auth = HTTPBasicAuth(username, password)
        headers = {'Accept': 'application/json'}
        
        # Get server info
        response = requests.get(f"{url}/rest/api/latest/info",
                               headers=headers, auth=auth, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('version', 'unknown')
            state = data.get('state', 'unknown')
            
            # Get plan count
            plans_resp = requests.get(f"{url}/rest/api/latest/plan",
                                     headers=headers, auth=auth, timeout=10)
            plan_count = 0
            if plans_resp.status_code == 200:
                plan_count = plans_resp.json().get('plans', {}).get('size', 0)
            
            # Get project count
            projects_resp = requests.get(f"{url}/rest/api/latest/project",
                                        headers=headers, auth=auth, timeout=10)
            project_count = 0
            if projects_resp.status_code == 200:
                project_count = projects_resp.json().get('projects', {}).get('size', 0)
            
            # Get agent count
            agents_resp = requests.get(f"{url}/rest/api/latest/agent",
                                      headers=headers, auth=auth, timeout=10)
            agent_count = 0
            if agents_resp.status_code == 200:
                agent_count = agents_resp.json().get('size', 0)
            
            return True, f"Successfully authenticated to Bamboo {version}\nState: {state}\nProjects: {project_count}\nPlans: {plan_count}\nAgents: {agent_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Bamboo error: {e}"

