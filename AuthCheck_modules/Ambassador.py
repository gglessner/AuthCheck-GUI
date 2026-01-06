# Ambassador / Emissary-ingress Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Ambassador / Emissary-ingress (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "admin_port", "type": "text", "label": "Admin Port", "default": "8877"},
    {"name": "protocol", "type": "combo", "label": "Protocol",
     "options": ["Gateway", "Admin Diagnostics"]},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Basic", "Bearer Token", "API Key"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password/Token/Key"},
    {"name": "api_key_header", "type": "text", "label": "API Key Header", "default": "X-API-Key"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Gateway: 8080/8443, Admin: 8877. Diagnostics: /ambassador/v0/diag/"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Ambassador / Emissary-ingress.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    admin_port = form_data.get('admin_port', '').strip()
    protocol = form_data.get('protocol', 'Gateway')
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    api_key_header = form_data.get('api_key_header', 'X-API-Key').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    scheme = "https" if use_https else "http"
    
    try:
        headers = {}
        auth = None
        
        if auth_type == "Basic" and username:
            auth = (username, password)
        elif auth_type == "Bearer Token" and password:
            headers['Authorization'] = f"Bearer {password}"
        elif auth_type == "API Key" and password:
            headers[api_key_header] = password
        
        if protocol == "Admin Diagnostics":
            url = f"http://{host}:{admin_port}/ambassador/v0/diag/"
            
            response = requests.get(url, auth=auth, headers=headers, verify=verify_ssl, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                version = data.get('ambassador_version', 'unknown')
                return True, f"Successfully connected to Ambassador Admin at {host}:{admin_port}\nVersion: {version}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            elif response.status_code == 404:
                return False, "Admin diagnostics not found"
            else:
                return False, f"Admin returned status {response.status_code}"
        else:
            url = f"{scheme}://{host}:{port}/"
            
            response = requests.get(url, auth=auth, headers=headers, verify=verify_ssl, timeout=10)
            
            server = response.headers.get('Server', '')
            
            if response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            elif response.status_code < 500:
                return True, f"Successfully connected to Ambassador Gateway at {host}:{port}\nServer: {server or 'Ambassador'}"
            else:
                return False, f"Gateway returned status {response.status_code}"
                
    except Exception as e:
        return False, f"Error: {e}"

