# Jetty Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Jetty (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Basic", "Digest", "Form"]},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "login_path", "type": "text", "label": "Login Path (Form)", "default": "/j_security_check"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "HTTP: 8080, HTTPS: 8443. admin / admin"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Jetty.
    """
    try:
        import requests
        from requests.auth import HTTPBasicAuth, HTTPDigestAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    login_path = form_data.get('login_path', '/j_security_check').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not port:
        return False, "Port is required"
    
    scheme = "https" if use_https else "http"
    base_url = f"{scheme}://{host}:{port}"
    
    try:
        session = requests.Session()
        
        if auth_type == "Basic":
            auth = HTTPBasicAuth(username, password)
            response = session.get(base_url, auth=auth, verify=verify_ssl, timeout=10)
        elif auth_type == "Digest":
            auth = HTTPDigestAuth(username, password)
            response = session.get(base_url, auth=auth, verify=verify_ssl, timeout=10)
        elif auth_type == "Form":
            response = session.post(
                f"{base_url}{login_path}",
                data={"j_username": username, "j_password": password},
                verify=verify_ssl,
                timeout=10,
                allow_redirects=True
            )
        else:
            response = session.get(base_url, verify=verify_ssl, timeout=10)
        
        server = response.headers.get('Server', '')
        
        if response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Access forbidden"
        elif response.status_code < 400:
            if 'Jetty' in server:
                return True, f"Successfully connected to Jetty at {base_url}\nServer: {server}"
            else:
                return True, f"Successfully connected to {base_url}\nServer: {server or 'unknown'}"
        else:
            return False, f"HTTP returned status {response.status_code}"
            
    except Exception as e:
        return False, f"Error: {e}"

