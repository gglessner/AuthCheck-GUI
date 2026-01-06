# Atlassian Confluence Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Atlassian Confluence (Collaboration)"

form_fields = [
    {"name": "url", "type": "text", "label": "Confluence URL"},
    {"name": "email", "type": "text", "label": "Email (Cloud) / Username (Server)"},
    {"name": "api_token", "type": "password", "label": "API Token (Cloud) / Password (Server)"},
    {"name": "deployment", "type": "combo", "label": "Deployment Type", "options": ["Cloud", "Server/Data Center"], "default": "Cloud"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Cloud: xxx.atlassian.net/wiki, API token from id.atlassian.com. Server: hostname:8090."},
]


def authenticate(form_data):
    """Attempt to authenticate to Atlassian Confluence."""
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
        return False, "Confluence URL is required"
    if not email:
        return False, "Email/Username is required"
    if not api_token:
        return False, "API Token/Password is required"
    
    if not url.startswith('http'):
        url = f"https://{url}"
    url = url.rstrip('/')
    
    # Cloud URLs need /wiki
    if deployment == "Cloud" and not url.endswith('/wiki'):
        url = f"{url}/wiki"
    
    try:
        auth = HTTPBasicAuth(email, api_token)
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Get current user
        response = requests.get(f"{url}/rest/api/user/current",
                               auth=auth, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            display_name = user_data.get('displayName', 'unknown')
            username = user_data.get('username', user_data.get('accountId', 'unknown'))
            
            # Get space count
            spaces_resp = requests.get(f"{url}/rest/api/space?limit=1",
                                       auth=auth, headers=headers, timeout=10)
            space_count = 0
            if spaces_resp.status_code == 200:
                space_count = spaces_resp.json().get('size', 0)
            
            # Get server info (for Server/DC)
            version = 'Cloud'
            if deployment == "Server/Data Center":
                # Try to get server info
                pass
            
            return True, f"Successfully authenticated to Confluence\nDeployment: {deployment}\nUser: {display_name} ({username})\nSpaces: {space_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Confluence error: {e}"

