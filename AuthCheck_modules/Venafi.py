# Venafi Trust Protection Platform Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Venafi TPP (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "Venafi TPP Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "client_id", "type": "text", "label": "Client ID (OAuth)"},
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Trust Protection Platform. Certificate and machine identity management."},
]


def authenticate(form_data):
    """Attempt to authenticate to Venafi TPP."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    client_id = form_data.get('client_id', '').strip()
    api_key = form_data.get('api_key', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Venafi TPP Host is required"
    
    try:
        base_url = f"https://{host}:{port}"
        session = requests.Session()
        session.verify = verify_ssl
        
        if api_key:
            # API key authentication
            headers = {
                'X-Venafi-Api-Key': api_key,
                'Content-Type': 'application/json'
            }
            
            response = session.get(
                f"{base_url}/vedsdk/Identity/Self",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                identity = response.json()
                name = identity.get('Name', 'unknown')
                
                return True, f"Successfully authenticated to Venafi TPP\nHost: {host}:{port}\nIdentity: {name}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid API key"
                
        elif username and password:
            if client_id:
                # OAuth authentication
                auth_resp = session.post(
                    f"{base_url}/vedauth/authorize/oauth",
                    json={
                        'username': username,
                        'password': password,
                        'client_id': client_id,
                        'scope': 'certificate:manage'
                    },
                    timeout=15
                )
            else:
                # Basic authentication
                auth_resp = session.post(
                    f"{base_url}/vedsdk/authorize",
                    json={
                        'Username': username,
                        'Password': password
                    },
                    timeout=15
                )
            
            if auth_resp.status_code == 200:
                token_data = auth_resp.json()
                token = token_data.get('APIKey', token_data.get('access_token'))
                
                if token:
                    headers = {'X-Venafi-Api-Key': token}
                    
                    # Get identity
                    id_resp = session.get(
                        f"{base_url}/vedsdk/Identity/Self",
                        headers=headers,
                        timeout=10
                    )
                    
                    identity_name = username
                    if id_resp.status_code == 200:
                        identity_name = id_resp.json().get('Name', username)
                    
                    # Get certificate count
                    certs_resp = session.get(
                        f"{base_url}/vedsdk/certificates?limit=1",
                        headers=headers,
                        timeout=10
                    )
                    cert_count = 0
                    if certs_resp.status_code == 200:
                        cert_count = certs_resp.json().get('TotalCount', 0)
                    
                    return True, f"Successfully authenticated to Venafi TPP\nHost: {host}:{port}\nIdentity: {identity_name}\nCertificates: {cert_count}"
                
                return True, f"Successfully authenticated to Venafi TPP\nHost: {host}:{port}"
            elif auth_resp.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            else:
                return False, f"HTTP {auth_resp.status_code}: {auth_resp.text[:200]}"
        else:
            return False, "Username/Password or API Key required"
            
    except Exception as e:
        return False, f"Venafi error: {e}"

