# Cisco Unity Connection Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Cisco Unity (PBX)"

form_fields = [
    {"name": "host", "type": "text", "label": "Unity Connection Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": "administrator"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: administrator/(configured). CUPI REST API."},
]


def authenticate(form_data):
    """Attempt to authenticate to Cisco Unity Connection."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Unity Connection Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        base_url = f"https://{host}:{port}"
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Try CUPI API - get version
        response = requests.get(
            f"{base_url}/vmrest/version",
            headers=headers,
            auth=(username, password),
            verify=verify_ssl,
            timeout=15
        )
        
        if response.status_code == 200:
            version_data = response.json()
            version = version_data.get('version', 'unknown')
            
            # Get user count
            users_resp = requests.get(
                f"{base_url}/vmrest/users?rowsPerPage=1",
                headers=headers,
                auth=(username, password),
                verify=verify_ssl,
                timeout=10
            )
            user_count = 0
            if users_resp.status_code == 200:
                users_data = users_resp.json()
                user_count = users_data.get('@total', 0)
            
            return True, f"Successfully authenticated to Cisco Unity Connection\nHost: {host}:{port}\nVersion: {version}\nUsers: {user_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Cisco Unity Connection error: {e}"

