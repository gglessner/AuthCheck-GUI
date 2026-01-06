# Apache HTTP Server Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache HTTP Server (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "80",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "protected_path", "type": "text", "label": "Protected Path", "default": "/"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Basic", "Digest"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 443, Non-TLS: 80. .htpasswd auth. Check httpd.conf."},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache HTTP Server.
    """
    try:
        import requests
        from requests.auth import HTTPBasicAuth, HTTPDigestAuth
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    protected_path = form_data.get('protected_path', '/').strip()
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else ("443" if use_https else "80")
        url = f"{scheme}://{host}:{port_num}{protected_path}"
        
        auth = None
        if auth_type == "Basic" and username:
            auth = HTTPBasicAuth(username, password)
        elif auth_type == "Digest" and username:
            auth = HTTPDigestAuth(username, password)
        
        response = requests.get(url, auth=auth, verify=verify_ssl, timeout=10)
        
        # Check server header
        server = response.headers.get('Server', 'Unknown')
        
        if response.status_code == 200:
            return True, f"Successfully authenticated to Apache HTTP Server\nServer: {server}\nPath: {protected_path}"
        elif response.status_code == 401:
            return False, f"Authentication failed: Unauthorized\nServer: {server}"
        elif response.status_code == 403:
            return False, f"Authentication failed: Forbidden\nServer: {server}"
        else:
            return False, f"HTTP {response.status_code}\nServer: {server}"
            
    except Exception as e:
        return False, f"HTTP Server error: {e}"

