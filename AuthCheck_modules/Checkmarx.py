# Checkmarx Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Checkmarx (Security)"

form_fields = [
    {"name": "url", "type": "text", "label": "Checkmarx URL"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "api_key", "type": "password", "label": "API Key (CxOne)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "CxSAST: username/password. CxOne: API key from IAM > API Keys."},
]


def authenticate(form_data):
    """Attempt to authenticate to Checkmarx."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    api_key = form_data.get('api_key', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not url:
        return False, "Checkmarx URL is required"
    
    if not url.startswith('http'):
        url = f"https://{url}"
    url = url.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        if api_key:
            # CxOne authentication
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Accept': 'application/json'
            }
            
            response = session.get(f"{url}/api/projects",
                                  headers=headers, timeout=15)
            
            if response.status_code == 200:
                projects = response.json()
                project_count = len(projects) if isinstance(projects, list) else 0
                
                return True, f"Successfully authenticated to Checkmarx One\nProjects: {project_count}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid API key"
            else:
                return False, f"HTTP {response.status_code}"
        else:
            # CxSAST authentication
            if not username:
                return False, "Username or API Key required"
            
            token_resp = session.post(
                f"{url}/cxrestapi/auth/identity/connect/token",
                data={
                    'username': username,
                    'password': password,
                    'grant_type': 'password',
                    'scope': 'sast_rest_api',
                    'client_id': 'resource_owner_client',
                    'client_secret': '014DF517-39D1-4453-B7B3-9930C563627C'
                },
                timeout=15
            )
            
            if token_resp.status_code == 200:
                access_token = token_resp.json().get('access_token')
                headers = {'Authorization': f'Bearer {access_token}'}
                
                # Get projects
                projects_resp = session.get(f"{url}/cxrestapi/projects",
                                           headers=headers, timeout=10)
                project_count = 0
                if projects_resp.status_code == 200:
                    project_count = len(projects_resp.json())
                
                return True, f"Successfully authenticated to Checkmarx SAST\nProjects: {project_count}"
            elif token_resp.status_code == 400:
                return False, "Authentication failed: Invalid credentials"
            else:
                return False, f"HTTP {token_resp.status_code}: {token_resp.text[:200]}"
            
    except Exception as e:
        return False, f"Checkmarx error: {e}"

