# Docker Registry Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Docker Registry (CI/CD)"

form_fields = [
    {"name": "registry", "type": "text", "label": "Registry URL", "default": "https://registry-1.docker.io"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password/Token"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Docker Hub: dockerhub_username / token. Private: admin / admin"},
]


def authenticate(form_data):
    """Attempt to authenticate to Docker Registry."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    registry = form_data.get('registry', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', True)
    
    if not registry:
        return False, "Registry URL is required"
    
    try:
        # Check v2 API
        url = f"{registry}/v2/"
        auth = HTTPBasicAuth(username, password) if username else None
        
        response = requests.get(url, auth=auth, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            # Get catalog
            catalog_resp = requests.get(f"{registry}/v2/_catalog", auth=auth,
                                       verify=verify_ssl, timeout=10)
            repos = []
            if catalog_resp.status_code == 200:
                repos = catalog_resp.json().get('repositories', [])[:10]
            
            return True, f"Successfully authenticated to Docker Registry\nRepositories: {repos}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, f"Registry error: {e}"

