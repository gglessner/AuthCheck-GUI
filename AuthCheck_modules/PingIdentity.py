# Ping Identity / PingFederate Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Ping Identity / PingFederate (IAM)"

form_fields = [
    {"name": "host", "type": "text", "label": "PingFederate Host"},
    {"name": "admin_port", "type": "text", "label": "Admin API Port", "default": "9999"},
    {"name": "username", "type": "text", "label": "Admin Username", "default": "Administrator"},
    {"name": "password", "type": "password", "label": "Admin Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Administrator / (set during install). Admin API on port 9999 by default."},
]


def authenticate(form_data):
    """Attempt to authenticate to PingFederate."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    admin_port = form_data.get('admin_port', '9999').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "PingFederate Host is required"
    if not username:
        return False, "Admin Username is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        base_url = f"{host}:{admin_port}/pf-admin-api/v1"
        auth = HTTPBasicAuth(username, password)
        headers = {
            'X-XSRF-Header': 'PingFederate',
            'Accept': 'application/json'
        }
        
        # Get version info
        response = requests.get(f"{base_url}/version",
                               auth=auth, headers=headers,
                               verify=verify_ssl, timeout=15)
        
        if response.status_code == 200:
            version = response.json().get('version', 'unknown')
            
            # Get server settings
            settings_resp = requests.get(f"{base_url}/serverSettings",
                                        auth=auth, headers=headers,
                                        verify=verify_ssl, timeout=10)
            federation_info = ""
            if settings_resp.status_code == 200:
                settings = settings_resp.json()
                fed_info = settings.get('federationInfo', {})
                base_url_display = fed_info.get('baseUrl', 'unknown')
                federation_info = f"\nBase URL: {base_url_display}"
            
            # Get SP connection count
            sp_resp = requests.get(f"{base_url}/idp/spConnections",
                                  auth=auth, headers=headers,
                                  verify=verify_ssl, timeout=10)
            sp_count = 0
            if sp_resp.status_code == 200:
                sp_count = len(sp_resp.json().get('items', []))
            
            # Get IdP connection count
            idp_resp = requests.get(f"{base_url}/sp/idpConnections",
                                   auth=auth, headers=headers,
                                   verify=verify_ssl, timeout=10)
            idp_count = 0
            if idp_resp.status_code == 200:
                idp_count = len(idp_resp.json().get('items', []))
            
            return True, f"Successfully authenticated to PingFederate {version}{federation_info}\nSP Connections: {sp_count}\nIdP Connections: {idp_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"PingFederate error: {e}"

