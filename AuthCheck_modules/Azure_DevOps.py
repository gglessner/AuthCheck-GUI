# Azure DevOps Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Azure DevOps (CI/CD)"

form_fields = [
    {"name": "organization", "type": "text", "label": "Organization"},
    {"name": "pat", "type": "password", "label": "Personal Access Token"},
    {"name": "project", "type": "text", "label": "Project (Optional)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "PAT from User Settings > Personal Access Tokens. Organization from URL: dev.azure.com/{org}"},
]


def authenticate(form_data):
    """Attempt to authenticate to Azure DevOps."""
    try:
        import requests
        import base64
    except ImportError:
        return False, "requests package not installed"
    
    organization = form_data.get('organization', '').strip()
    pat = form_data.get('pat', '').strip()
    project = form_data.get('project', '').strip()
    
    if not organization:
        return False, "Organization is required"
    if not pat:
        return False, "Personal Access Token is required"
    
    try:
        # PAT uses Basic Auth with empty username
        auth_string = base64.b64encode(f":{pat}".encode()).decode()
        headers = {
            'Authorization': f'Basic {auth_string}',
            'Content-Type': 'application/json'
        }
        
        base_url = f"https://dev.azure.com/{organization}"
        
        # Get projects
        response = requests.get(f"{base_url}/_apis/projects?api-version=7.0",
                               headers=headers, timeout=15)
        
        if response.status_code == 200:
            projects = response.json().get('value', [])
            project_count = len(projects)
            project_names = [p['name'] for p in projects[:3]]
            
            if project:
                # Get specific project info
                proj_resp = requests.get(f"{base_url}/{project}/_apis/build/builds?api-version=7.0&$top=1",
                                        headers=headers, timeout=10)
                build_count = 0
                if proj_resp.status_code == 200:
                    build_count = proj_resp.json().get('count', 0)
                
                repos_resp = requests.get(f"{base_url}/{project}/_apis/git/repositories?api-version=7.0",
                                         headers=headers, timeout=10)
                repo_count = 0
                if repos_resp.status_code == 200:
                    repo_count = len(repos_resp.json().get('value', []))
                
                return True, f"Successfully authenticated to Azure DevOps\nOrganization: {organization}\nProject: {project}\nRepos: {repo_count}\nBuilds: {build_count}"
            
            return True, f"Successfully authenticated to Azure DevOps\nOrganization: {organization}\nProjects: {project_count}\nSample: {', '.join(project_names)}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid PAT"
        elif response.status_code == 404:
            return False, "Organization not found"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Azure DevOps error: {e}"

