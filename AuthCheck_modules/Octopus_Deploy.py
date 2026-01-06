# Octopus Deploy Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Octopus Deploy (CI/CD)"

form_fields = [
    {"name": "url", "type": "text", "label": "Octopus URL"},
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API key from Profile > My API Keys. Default port 80/443."},
]


def authenticate(form_data):
    """Attempt to authenticate to Octopus Deploy."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', '').strip()
    api_key = form_data.get('api_key', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not url:
        return False, "Octopus URL is required"
    if not api_key:
        return False, "API Key is required"
    
    if not url.startswith('http'):
        url = f"https://{url}"
    url = url.rstrip('/')
    
    try:
        headers = {
            'X-Octopus-ApiKey': api_key,
            'Accept': 'application/json'
        }
        
        # Get server status
        response = requests.get(
            f"{url}/api",
            headers=headers,
            verify=verify_ssl,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('Version', 'unknown')
            
            # Get current user
            me_resp = requests.get(
                f"{url}/api/users/me",
                headers=headers,
                verify=verify_ssl,
                timeout=10
            )
            user_info = ""
            if me_resp.status_code == 200:
                user = me_resp.json()
                username = user.get('Username', 'unknown')
                is_active = user.get('IsActive', False)
                user_info = f"\nUser: {username}\nActive: {is_active}"
            
            # Get projects count
            projects_resp = requests.get(
                f"{url}/api/projects/all",
                headers=headers,
                verify=verify_ssl,
                timeout=10
            )
            project_count = 0
            if projects_resp.status_code == 200:
                project_count = len(projects_resp.json())
            
            # Get environments count
            envs_resp = requests.get(
                f"{url}/api/environments/all",
                headers=headers,
                verify=verify_ssl,
                timeout=10
            )
            env_count = 0
            if envs_resp.status_code == 200:
                env_count = len(envs_resp.json())
            
            return True, f"Successfully authenticated to Octopus Deploy\nURL: {url}\nVersion: {version}{user_info}\nProjects: {project_count}\nEnvironments: {env_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API key"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Octopus Deploy error: {e}"

