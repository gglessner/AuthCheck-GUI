# Voltage SecureData Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Voltage SecureData (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "Voltage Server"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "identity", "type": "text", "label": "Identity (for IBE)"},
    {"name": "shared_secret", "type": "password", "label": "Shared Secret"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "OpenText/Micro Focus. Format-Preserving Encryption, tokenization. REST API."},
]


def authenticate(form_data):
    """Attempt to authenticate to Voltage SecureData."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    identity = form_data.get('identity', '').strip()
    shared_secret = form_data.get('shared_secret', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Voltage Server is required"
    
    try:
        base_url = f"https://{host}:{port}"
        session = requests.Session()
        session.verify = verify_ssl
        
        # Try REST API authentication
        if username and password:
            # Username/password authentication
            auth_url = f"{base_url}/vibesimple/rest/v1/authenticate"
            
            response = session.post(
                auth_url,
                json={'username': username, 'password': password},
                timeout=15
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                token = auth_data.get('token', auth_data.get('sessionId'))
                
                if token:
                    # Get server info
                    headers = {'Authorization': f'Bearer {token}'}
                    
                    info_resp = session.get(
                        f"{base_url}/vibesimple/rest/v1/info",
                        headers=headers,
                        timeout=10
                    )
                    
                    version = 'unknown'
                    if info_resp.status_code == 200:
                        info = info_resp.json()
                        version = info.get('version', 'unknown')
                    
                    return True, f"Successfully authenticated to Voltage SecureData\nHost: {host}:{port}\nVersion: {version}\nSession: Active"
                
                return True, f"Successfully authenticated to Voltage SecureData\nHost: {host}:{port}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
        
        elif identity and shared_secret:
            # Identity-Based Encryption (IBE) authentication
            auth_url = f"{base_url}/vibesimple/rest/v1/fetchkey"
            
            response = session.post(
                auth_url,
                json={
                    'identity': identity,
                    'sharedSecret': shared_secret
                },
                timeout=15
            )
            
            if response.status_code == 200:
                return True, f"Successfully authenticated to Voltage SecureData (IBE)\nHost: {host}:{port}\nIdentity: {identity}\nKey fetch: Successful"
            elif response.status_code == 401 or response.status_code == 403:
                return False, "Authentication failed: Invalid identity or shared secret"
        
        else:
            # Try to access server info endpoint without auth
            info_resp = session.get(
                f"{base_url}/vibesimple/rest/v1/info",
                timeout=10
            )
            
            if info_resp.status_code == 200:
                info = info_resp.json()
                version = info.get('version', 'unknown')
                return True, f"Connected to Voltage SecureData\nHost: {host}:{port}\nVersion: {version}\nNote: No authentication required for info endpoint"
            elif info_resp.status_code == 401:
                return False, "Username/password or Identity/SharedSecret required"
            else:
                return False, f"HTTP {info_resp.status_code}"
        
        return False, f"Could not authenticate to {host}"
            
    except Exception as e:
        return False, f"Voltage SecureData error: {e}"

