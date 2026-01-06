# GitLab Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "GitLab (CI/CD)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "gitlab.com"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["Personal Access Token", "OAuth Token", "Private Token"]},
    {"name": "token", "type": "password", "label": "Token"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "HTTPS: 443, HTTP: 80. PAT from User Settings > Access Tokens."},
]


def authenticate(form_data):
    """Attempt to authenticate to GitLab."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    use_https = form_data.get('use_https', True)
    auth_type = form_data.get('auth_type', 'Personal Access Token')
    token = form_data.get('token', '').strip()
    verify_ssl = form_data.get('verify_ssl', True)
    
    if not host:
        return False, "Host is required"
    if not token:
        return False, "Token is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}/api/v4"
        
        headers = {}
        if auth_type in ["Personal Access Token", "Private Token"]:
            headers['PRIVATE-TOKEN'] = token
        else:
            headers['Authorization'] = f"Bearer {token}"
        
        # Get current user
        response = requests.get(f"{base_url}/user", headers=headers,
                               verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            user = response.json()
            username = user.get('username', 'unknown')
            is_admin = user.get('is_admin', False)
            
            # Get projects count
            proj_resp = requests.get(f"{base_url}/projects?per_page=1", headers=headers,
                                    verify=verify_ssl, timeout=10)
            projects = int(proj_resp.headers.get('X-Total', 0)) if proj_resp.status_code == 200 else 0
            
            admin_str = " (Admin)" if is_admin else ""
            return True, f"Successfully authenticated to GitLab\nUser: {username}{admin_str}\nProjects: {projects}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, f"GitLab error: {e}"

