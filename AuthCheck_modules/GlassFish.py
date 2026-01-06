# GlassFish/Payara Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "GlassFish / Payara (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "admin_port", "type": "text", "label": "Admin Port", "default": "4848",
     "port_toggle": "use_https", "tls_port": "4848", "non_tls_port": "4848"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Admin: 4848 (TLS/non-TLS same). admin / (empty)"},
]


def authenticate(form_data):
    """Attempt to authenticate to GlassFish/Payara."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    admin_port = form_data.get('admin_port', '4848').strip()
    use_https = form_data.get('use_https', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{admin_port}"
        
        auth = HTTPBasicAuth(username, password) if username else None
        headers = {
            'Accept': 'application/json',
            'X-Requested-By': 'authcheck'
        }
        
        # Get domain info
        url = f"{base_url}/management/domain"
        response = requests.get(url, auth=auth, headers=headers, 
                               verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Get applications
            apps_url = f"{base_url}/management/domain/applications/application"
            apps_resp = requests.get(apps_url, auth=auth, headers=headers,
                                    verify=verify_ssl, timeout=10)
            apps = []
            if apps_resp.status_code == 200:
                apps_data = apps_resp.json()
                apps = list(apps_data.get('extraProperties', {}).get('childResources', {}).keys())
            
            # Detect if Payara or GlassFish
            server_name = "GlassFish/Payara"
            
            return True, f"Successfully authenticated to {server_name} at {host}:{admin_port}\nApplications: {apps}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, f"GlassFish error: {e}"

