# Jenkins Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Jenkins (CI/CD)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password/API Token"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8443, Non-TLS: 8080. admin / (initial in secrets/)"},
]


def authenticate(form_data):
    """Attempt to authenticate to Jenkins."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8080').strip()
    use_https = form_data.get('use_https', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        auth = HTTPBasicAuth(username, password) if username else None
        
        # Get API info
        response = requests.get(f"{base_url}/api/json", auth=auth,
                               verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            jobs = data.get('jobs', [])
            views = data.get('views', [])
            
            # Get version from header
            version = response.headers.get('X-Jenkins', 'unknown')
            
            return True, f"Successfully authenticated to Jenkins {version}\nJobs: {len(jobs)}, Views: {len(views)}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, f"Jenkins error: {e}"

