# Thales CipherTrust Manager Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Thales CipherTrust Manager (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "CipherTrust Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "domain", "type": "text", "label": "Domain", "default": "root"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: admin/(configured). Formerly Vormetric/Gemalto. Key management."},
]


def authenticate(form_data):
    """Attempt to authenticate to Thales CipherTrust Manager."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    domain = form_data.get('domain', 'root').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "CipherTrust Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        base_url = f"https://{host}:{port}"
        
        # Authenticate to get token
        auth_resp = requests.post(
            f"{base_url}/api/v1/auth/tokens",
            json={
                'username': username,
                'password': password,
                'domain': domain
            },
            verify=verify_ssl,
            timeout=15
        )
        
        if auth_resp.status_code in [200, 201]:
            token_data = auth_resp.json()
            token = token_data.get('jwt', token_data.get('token'))
            
            headers = {'Authorization': f'Bearer {token}'}
            
            # Get system info
            sys_resp = requests.get(
                f"{base_url}/api/v1/system/info",
                headers=headers,
                verify=verify_ssl,
                timeout=10
            )
            
            version = 'unknown'
            if sys_resp.status_code == 200:
                sys_info = sys_resp.json()
                version = sys_info.get('version', 'unknown')
            
            # Get user info
            user_resp = requests.get(
                f"{base_url}/api/v1/usermgmt/users/self",
                headers=headers,
                verify=verify_ssl,
                timeout=10
            )
            
            user_info = ""
            if user_resp.status_code == 200:
                user = user_resp.json()
                user_name = user.get('username', username)
                user_info = f"\nUser: {user_name}"
            
            # Get key count
            keys_resp = requests.get(
                f"{base_url}/api/v1/vault/keys2?limit=1",
                headers=headers,
                verify=verify_ssl,
                timeout=10
            )
            
            key_count = 0
            if keys_resp.status_code == 200:
                key_count = keys_resp.json().get('total', 0)
            
            return True, f"Successfully authenticated to Thales CipherTrust\nHost: {host}:{port}\nVersion: {version}{user_info}\nDomain: {domain}\nKeys: {key_count}"
        elif auth_resp.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {auth_resp.status_code}: {auth_resp.text[:200]}"
            
    except Exception as e:
        return False, f"Thales CipherTrust error: {e}"

