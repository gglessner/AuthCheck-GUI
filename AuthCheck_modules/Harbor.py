# Harbor Container Registry Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Harbor Registry (Container)"

form_fields = [
    {"name": "url", "type": "text", "label": "Harbor URL"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / Harbor12345 (default). Change password on first login."},
]


def authenticate(form_data):
    """Attempt to authenticate to Harbor Registry."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not url:
        return False, "Harbor URL is required"
    if not username:
        return False, "Username is required"
    
    if not url.startswith('http'):
        url = f"https://{url}"
    url = url.rstrip('/')
    
    try:
        auth = HTTPBasicAuth(username, password)
        headers = {'Accept': 'application/json'}
        session = requests.Session()
        session.verify = verify_ssl
        
        # Get system info
        response = session.get(f"{url}/api/v2.0/systeminfo",
                              headers=headers, auth=auth, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('harbor_version', 'unknown')
            
            # Get project count
            projects_resp = session.get(f"{url}/api/v2.0/projects",
                                       headers=headers, auth=auth, timeout=10)
            project_count = 0
            if projects_resp.status_code == 200:
                project_count = len(projects_resp.json())
            
            # Get repository count
            repos_resp = session.get(f"{url}/api/v2.0/repositories",
                                    headers=headers, auth=auth, timeout=10)
            repo_count = 0
            if repos_resp.status_code == 200:
                repo_count = len(repos_resp.json())
            
            # Get user count
            users_resp = session.get(f"{url}/api/v2.0/users",
                                    headers=headers, auth=auth, timeout=10)
            user_count = 0
            if users_resp.status_code == 200:
                user_count = len(users_resp.json())
            
            return True, f"Successfully authenticated to Harbor {version}\nProjects: {project_count}\nRepositories: {repo_count}\nUsers: {user_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Harbor error: {e}"

