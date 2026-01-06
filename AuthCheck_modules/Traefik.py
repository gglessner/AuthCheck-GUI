# Traefik Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Traefik (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "api_port", "type": "text", "label": "API Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Basic Auth", "Digest Auth"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8443, Non-TLS: 8080. Default: no auth. Basic if enabled."},
]


def authenticate(form_data):
    """Attempt to authenticate to Traefik API."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth, HTTPDigestAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    api_port = form_data.get('api_port', '8080').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{api_port}/api"
        
        auth = None
        if auth_type == "Basic Auth" and username:
            auth = HTTPBasicAuth(username, password)
        elif auth_type == "Digest Auth" and username:
            auth = HTTPDigestAuth(username, password)
        
        response = requests.get(f"{base_url}/version", auth=auth, 
                               verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('Version', 'unknown')
            
            # Get overview
            overview_resp = requests.get(f"{base_url}/overview", auth=auth,
                                        verify=verify_ssl, timeout=10)
            if overview_resp.status_code == 200:
                overview = overview_resp.json()
                http_info = overview.get('http', {})
                routers = http_info.get('routers', {}).get('total', 0)
                services = http_info.get('services', {}).get('total', 0)
                
                return True, f"Successfully connected to Traefik {version}\nRouters: {routers}, Services: {services}"
            
            return True, f"Successfully connected to Traefik {version}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, f"Traefik error: {e}"

