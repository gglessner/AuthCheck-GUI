# HAProxy Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "HAProxy (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "stats_port", "type": "text", "label": "Stats Port", "default": "8404",
     "port_toggle": "use_https", "tls_port": "8404", "non_tls_port": "8404"},
    {"name": "stats_path", "type": "text", "label": "Stats Path", "default": "/stats"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Stats: 8404 (TLS/non-TLS same). admin / admin if enabled."},
]


def authenticate(form_data):
    """Attempt to authenticate to HAProxy stats page."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    stats_port = form_data.get('stats_port', '8404').strip()
    stats_path = form_data.get('stats_path', '/stats').strip()
    use_https = form_data.get('use_https', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        url = f"{scheme}://{host}:{stats_port}{stats_path};json"
        
        auth = HTTPBasicAuth(username, password) if username else None
        
        response = requests.get(url, auth=auth, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Count backends and frontends
            frontends = 0
            backends = 0
            servers = 0
            
            for item in data:
                obj_type = item.get('objType', '')
                if obj_type == 'Frontend':
                    frontends += 1
                elif obj_type == 'Backend':
                    backends += 1
                elif obj_type == 'Server':
                    servers += 1
            
            return True, f"Successfully connected to HAProxy at {host}:{stats_port}\nFrontends: {frontends}, Backends: {backends}, Servers: {servers}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        elif response.status_code == 403:
            return False, "Access forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, f"HAProxy error: {e}"

