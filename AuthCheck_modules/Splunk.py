# Splunk Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Splunk (Monitoring)"

form_fields = [
    {"name": "host", "type": "text", "label": "Splunk Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Management Port", "default": "8089",
     "port_toggle": "verify_ssl", "tls_port": "8089", "non_tls_port": "8089"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "token", "type": "password", "label": "Auth Token (Alternative)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API: 8089 (TLS default). admin / changeme (change on first login)."},
]


def authenticate(form_data):
    """Attempt to authenticate to Splunk."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8089').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    token = form_data.get('token', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Splunk Host is required"
    
    try:
        base_url = f"https://{host}:{port}"
        
        if token:
            # Use token auth
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(f"{base_url}/services/authentication/current-context",
                                   headers=headers, verify=verify_ssl, timeout=10,
                                   params={'output_mode': 'json'})
        else:
            # Use username/password
            if not username:
                return False, "Username or Token is required"
            response = requests.get(f"{base_url}/services/authentication/current-context",
                                   auth=(username, password), verify=verify_ssl, timeout=10,
                                   params={'output_mode': 'json'})
        
        if response.status_code == 200:
            data = response.json()
            current_user = data['entry'][0]['content'].get('username', 'unknown')
            roles = data['entry'][0]['content'].get('roles', [])
            
            # Get server info
            if token:
                info_resp = requests.get(f"{base_url}/services/server/info",
                                        headers=headers, verify=verify_ssl, timeout=10,
                                        params={'output_mode': 'json'})
            else:
                info_resp = requests.get(f"{base_url}/services/server/info",
                                        auth=(username, password), verify=verify_ssl, timeout=10,
                                        params={'output_mode': 'json'})
            
            version = 'unknown'
            server_name = 'unknown'
            if info_resp.status_code == 200:
                info_data = info_resp.json()
                version = info_data['entry'][0]['content'].get('version', 'unknown')
                server_name = info_data['entry'][0]['content'].get('serverName', 'unknown')
            
            return True, f"Successfully authenticated to Splunk {version}\nServer: {server_name}\nUser: {current_user}\nRoles: {', '.join(roles)}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Splunk error: {e}"

