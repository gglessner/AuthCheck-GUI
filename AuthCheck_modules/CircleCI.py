# CircleCI Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "CircleCI (CI/CD)"

form_fields = [
    {"name": "token", "type": "password", "label": "API Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Personal API Token from User Settings > Personal API Tokens."},
]


def authenticate(form_data):
    """Attempt to authenticate to CircleCI."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    token = form_data.get('token', '').strip()
    
    if not token:
        return False, "API Token is required"
    
    try:
        headers = {'Circle-Token': token}
        
        # Get user info
        response = requests.get("https://circleci.com/api/v2/me",
                               headers=headers, timeout=15)
        
        if response.status_code == 200:
            user = response.json()
            username = user.get('login', 'unknown')
            user_id = user.get('id', 'unknown')
            
            # Get project count
            projects_resp = requests.get("https://circleci.com/api/v2/insights/pages/summary",
                                        headers=headers, timeout=10)
            
            # Get pipelines
            pipelines_resp = requests.get(f"https://circleci.com/api/v2/pipeline?mine=true",
                                         headers=headers, timeout=10)
            pipeline_count = 0
            if pipelines_resp.status_code == 200:
                pipeline_count = len(pipelines_resp.json().get('items', []))
            
            return True, f"Successfully authenticated to CircleCI\nUser: {username}\nUser ID: {user_id}\nRecent Pipelines: {pipeline_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"CircleCI error: {e}"

