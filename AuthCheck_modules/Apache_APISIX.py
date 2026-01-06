# Apache APISIX Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache APISIX (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "admin_port", "type": "text", "label": "Admin API Port", "default": "9180"},
    {"name": "gateway_port", "type": "text", "label": "Gateway Port", "default": "9080",
     "port_toggle": "use_https", "tls_port": "9443", "non_tls_port": "9080"},
    {"name": "protocol", "type": "combo", "label": "Protocol",
     "options": ["Admin API", "Gateway"]},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "api_key", "type": "password", "label": "Admin API Key"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Admin: 9180, Gateway: 9080/9443. Default key: edd1c9f034335f136f87ad84b625c8f1"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache APISIX.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    admin_port = form_data.get('admin_port', '').strip()
    gateway_port = form_data.get('gateway_port', '').strip()
    protocol = form_data.get('protocol', 'Admin API')
    use_https = form_data.get('use_https', False)
    api_key = form_data.get('api_key', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        if protocol == "Admin API":
            scheme = "https" if use_https else "http"
            url = f"{scheme}://{host}:{admin_port}/apisix/admin/routes"
            
            headers = {}
            if api_key:
                headers['X-API-KEY'] = api_key
            
            response = requests.get(url, headers=headers, verify=verify_ssl, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('list', data.get('node', {}).get('nodes', [])))
                return True, f"Successfully authenticated to APISIX Admin API at {host}:{admin_port}\nRoutes: {count}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid API key"
            else:
                return False, f"Admin API returned status {response.status_code}"
        else:
            scheme = "https" if use_https else "http"
            url = f"{scheme}://{host}:{gateway_port}/"
            
            response = requests.get(url, verify=verify_ssl, timeout=10)
            
            server = response.headers.get('Server', '')
            if 'APISIX' in server or response.status_code < 500:
                return True, f"Successfully connected to APISIX Gateway at {host}:{gateway_port}\nServer: {server or 'APISIX'}"
            else:
                return False, f"Gateway returned status {response.status_code}"
                
    except Exception as e:
        return False, f"Error: {e}"

