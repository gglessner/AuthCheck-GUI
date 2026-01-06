# JFrog Artifactory Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "JFrog Artifactory (CI/CD)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8082",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8082"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["Basic Auth", "API Key", "Access Token"]},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password/Key/Token"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8443, Non-TLS: 8082. admin / password"},
]


def authenticate(form_data):
    """Attempt to authenticate to JFrog Artifactory."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8082').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'Basic Auth')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{port}/artifactory/api"
        
        headers = {}
        auth = None
        
        if auth_type == "Basic Auth":
            auth = HTTPBasicAuth(username, password)
        elif auth_type == "API Key":
            headers['X-JFrog-Art-Api'] = password
        elif auth_type == "Access Token":
            headers['Authorization'] = f"Bearer {password}"
        
        # Get system info
        response = requests.get(f"{base_url}/system/ping", auth=auth, headers=headers,
                               verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            # Get version
            ver_resp = requests.get(f"{base_url}/system/version", auth=auth, headers=headers,
                                   verify=verify_ssl, timeout=10)
            version = 'unknown'
            if ver_resp.status_code == 200:
                version = ver_resp.json().get('version', 'unknown')
            
            # Get repos
            repos_resp = requests.get(f"{base_url}/repositories", auth=auth, headers=headers,
                                     verify=verify_ssl, timeout=10)
            repos = len(repos_resp.json()) if repos_resp.status_code == 200 else 0
            
            return True, f"Successfully authenticated to Artifactory {version}\nRepositories: {repos}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, f"Artifactory error: {e}"

