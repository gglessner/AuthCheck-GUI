# Keycloak Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Keycloak (IAM)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "realm", "type": "text", "label": "Realm", "default": "master"},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": "admin-cli"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8443, Non-TLS: 8080. admin / admin (set during setup)"},
]


def authenticate(form_data):
    """Attempt to authenticate to Keycloak."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8080').strip()
    use_https = form_data.get('use_https', False)
    realm = form_data.get('realm', 'master').strip()
    client_id = form_data.get('client_id', 'admin-cli').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        # Get token
        token_url = f"{base_url}/realms/{realm}/protocol/openid-connect/token"
        token_data = {
            'grant_type': 'password',
            'client_id': client_id,
            'username': username,
            'password': password
        }
        
        token_resp = requests.post(token_url, data=token_data, verify=verify_ssl, timeout=10)
        
        if token_resp.status_code == 200:
            token = token_resp.json().get('access_token')
            headers = {'Authorization': f"Bearer {token}"}
            
            # Get server info
            info_url = f"{base_url}/admin/realms/{realm}"
            info_resp = requests.get(info_url, headers=headers, verify=verify_ssl, timeout=10)
            
            if info_resp.status_code == 200:
                realm_data = info_resp.json()
                realm_name = realm_data.get('realm', realm)
                
                # Get users count
                users_url = f"{base_url}/admin/realms/{realm}/users/count"
                users_resp = requests.get(users_url, headers=headers, verify=verify_ssl, timeout=10)
                users = users_resp.json() if users_resp.status_code == 200 else 0
                
                # Get clients count
                clients_url = f"{base_url}/admin/realms/{realm}/clients"
                clients_resp = requests.get(clients_url, headers=headers, verify=verify_ssl, timeout=10)
                clients = len(clients_resp.json()) if clients_resp.status_code == 200 else 0
                
                return True, f"Successfully authenticated to Keycloak\nRealm: {realm_name}\nUsers: {users}, Clients: {clients}"
            
            return True, f"Successfully authenticated to Keycloak (realm: {realm})"
        elif token_resp.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            error = token_resp.json().get('error_description', token_resp.text[:200])
            return False, f"Authentication failed: {error}"
    except Exception as e:
        return False, f"Keycloak error: {e}"

