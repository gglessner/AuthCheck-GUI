# Jaeger Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Jaeger Tracing (Monitoring)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "query_port", "type": "text", "label": "Query Port", "default": "16686",
     "port_toggle": "use_https", "tls_port": "16686", "non_tls_port": "16686"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Basic Auth", "Bearer Token"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password/Token"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Query: 16686 (TLS/non-TLS same). Default: no auth."},
]


def authenticate(form_data):
    """Attempt to connect to Jaeger Query service."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    query_port = form_data.get('query_port', '16686').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{query_port}/api"
        
        auth = None
        headers = {}
        
        if auth_type == "Basic Auth" and username:
            auth = HTTPBasicAuth(username, password)
        elif auth_type == "Bearer Token" and password:
            headers['Authorization'] = f"Bearer {password}"
        
        # Get services
        response = requests.get(f"{base_url}/services", auth=auth, headers=headers,
                               verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            services = data.get('data', [])
            
            return True, f"Successfully connected to Jaeger at {host}:{query_port}\nServices: {len(services)}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, f"Jaeger error: {e}"

