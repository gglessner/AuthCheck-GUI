# SonarQube Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "SonarQube (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "9000",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "9000"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["Token", "User/Password"]},
    {"name": "token", "type": "password", "label": "Token"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 443, Non-TLS: 9000. admin / admin (change on first login)"},
]


def authenticate(form_data):
    """Attempt to authenticate to SonarQube."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '9000').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'Token')
    token = form_data.get('token', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{port}/api"
        
        if auth_type == "Token":
            auth = HTTPBasicAuth(token, '')
        else:
            auth = HTTPBasicAuth(username, password)
        
        # Get system status
        response = requests.get(f"{base_url}/system/status", auth=auth,
                               verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')
            version = data.get('version', 'unknown')
            
            # Get projects count
            proj_resp = requests.get(f"{base_url}/projects/search?ps=1", auth=auth,
                                    verify=verify_ssl, timeout=10)
            projects = 0
            if proj_resp.status_code == 200:
                projects = proj_resp.json().get('paging', {}).get('total', 0)
            
            return True, f"Successfully authenticated to SonarQube {version}\nStatus: {status}\nProjects: {projects}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, f"SonarQube error: {e}"

