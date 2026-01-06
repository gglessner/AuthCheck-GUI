# Snyk Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Snyk (Security)"

form_fields = [
    {"name": "api_token", "type": "password", "label": "API Token"},
    {"name": "org_id", "type": "text", "label": "Organization ID (Optional)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API token from Account Settings > API Token. Org ID from Settings > General."},
]


def authenticate(form_data):
    """Attempt to authenticate to Snyk."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    api_token = form_data.get('api_token', '').strip()
    org_id = form_data.get('org_id', '').strip()
    
    if not api_token:
        return False, "API Token is required"
    
    try:
        headers = {
            'Authorization': f'token {api_token}',
            'Content-Type': 'application/json'
        }
        
        # Get user info
        response = requests.get(
            "https://api.snyk.io/rest/self?version=2024-01-04",
            headers=headers, timeout=15
        )
        
        if response.status_code == 200:
            user = response.json().get('data', {}).get('attributes', {})
            username = user.get('username', 'unknown')
            email = user.get('email', 'unknown')
            
            # Get orgs
            orgs_resp = requests.get(
                "https://api.snyk.io/rest/orgs?version=2024-01-04",
                headers=headers, timeout=10
            )
            org_count = 0
            if orgs_resp.status_code == 200:
                org_count = len(orgs_resp.json().get('data', []))
            
            if org_id:
                # Get projects for specific org
                projects_resp = requests.get(
                    f"https://api.snyk.io/rest/orgs/{org_id}/projects?version=2024-01-04",
                    headers=headers, timeout=10
                )
                project_count = 0
                if projects_resp.status_code == 200:
                    project_count = len(projects_resp.json().get('data', []))
                
                return True, f"Successfully authenticated to Snyk\nUser: {username} ({email})\nOrganization: {org_id}\nProjects: {project_count}"
            
            return True, f"Successfully authenticated to Snyk\nUser: {username} ({email})\nOrganizations: {org_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Snyk error: {e}"

