# Bitbucket Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Bitbucket (CI/CD)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "bitbucket.org"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "server_type", "type": "combo", "label": "Server Type",
     "options": ["Bitbucket Cloud", "Bitbucket Server/DC"]},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "App Password/Token"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "HTTPS: 443, HTTP: 80. admin / admin (Server/DC)."},
]


def authenticate(form_data):
    """Attempt to authenticate to Bitbucket."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    server_type = form_data.get('server_type', 'Bitbucket Cloud')
    use_https = form_data.get('use_https', True)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', True)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        scheme = "https" if use_https else "http"
        auth = HTTPBasicAuth(username, password)
        
        if server_type == "Bitbucket Cloud":
            base_url = f"{scheme}://api.bitbucket.org/2.0"
            
            response = requests.get(f"{base_url}/user", auth=auth,
                                   verify=verify_ssl, timeout=10)
            
            if response.status_code == 200:
                user = response.json()
                display_name = user.get('display_name', username)
                
                return True, f"Successfully authenticated to Bitbucket Cloud\nUser: {display_name}"
        else:
            base_url = f"{scheme}://{host}/rest/api/1.0"
            
            response = requests.get(f"{base_url}/application-properties", auth=auth,
                                   verify=verify_ssl, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                version = data.get('version', 'unknown')
                
                return True, f"Successfully authenticated to Bitbucket Server {version}"
        
        if response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, f"Bitbucket error: {e}"

