# Lightstep (ServiceNow Cloud Observability) Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Lightstep (Monitoring)"

form_fields = [
    {"name": "organization", "type": "text", "label": "Organization"},
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API key from Account Settings > API Keys. Now part of ServiceNow Cloud Observability."},
]


def authenticate(form_data):
    """Attempt to authenticate to Lightstep."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    organization = form_data.get('organization', '').strip()
    api_key = form_data.get('api_key', '').strip()
    
    if not organization:
        return False, "Organization is required"
    if not api_key:
        return False, "API Key is required"
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }
        
        # Get projects
        response = requests.get(
            f"https://api.lightstep.com/public/v0.2/{organization}/projects",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            projects = data.get('data', [])
            project_count = len(projects)
            project_names = [p.get('attributes', {}).get('name', 'unknown') for p in projects[:5]]
            
            return True, f"Successfully authenticated to Lightstep\nOrganization: {organization}\nProjects: {project_count}\nSample: {', '.join(project_names) if project_names else 'none'}"
        elif response.status_code == 401 or response.status_code == 403:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Lightstep error: {e}"

