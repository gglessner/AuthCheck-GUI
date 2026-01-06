# Grafana Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Grafana (Monitoring)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "3000",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "3000"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["Basic Auth", "API Key", "Bearer Token"]},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password/API Key"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 443, Non-TLS: 3000. admin / admin"},
]


def authenticate(form_data):
    """Attempt to authenticate to Grafana."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '3000').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'Basic Auth')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{port}/api"
        
        auth = None
        headers = {}
        
        if auth_type == "Basic Auth":
            auth = HTTPBasicAuth(username, password)
        elif auth_type == "API Key":
            headers['Authorization'] = f"Bearer {password}"
        elif auth_type == "Bearer Token":
            headers['Authorization'] = f"Bearer {password}"
        
        # Get current user/org
        response = requests.get(f"{base_url}/org", auth=auth, headers=headers,
                               verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            org_data = response.json()
            org_name = org_data.get('name', 'unknown')
            
            # Get health
            health_resp = requests.get(f"{base_url}/health", verify=verify_ssl, timeout=10)
            version = 'unknown'
            if health_resp.status_code == 200:
                version = health_resp.json().get('version', 'unknown')
            
            # Get dashboards count
            search_resp = requests.get(f"{base_url}/search?type=dash-db", auth=auth,
                                      headers=headers, verify=verify_ssl, timeout=10)
            dashboards = 0
            if search_resp.status_code == 200:
                dashboards = len(search_resp.json())
            
            # Get datasources
            ds_resp = requests.get(f"{base_url}/datasources", auth=auth,
                                  headers=headers, verify=verify_ssl, timeout=10)
            datasources = 0
            if ds_resp.status_code == 200:
                datasources = len(ds_resp.json())
            
            return True, f"Successfully authenticated to Grafana {version}\nOrg: {org_name}\nDashboards: {dashboards}, Datasources: {datasources}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, f"Grafana error: {e}"

