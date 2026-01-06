# NGINX Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "NGINX / NGINX Plus (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "80",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "status_path", "type": "text", "label": "Status Path", "default": "/nginx_status"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "is_plus", "type": "checkbox", "label": "NGINX Plus (API)"},
    {"name": "api_path", "type": "text", "label": "API Path (Plus)", "default": "/api"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 443, Non-TLS: 80. Auth via .htpasswd."},
]


def authenticate(form_data):
    """Attempt to authenticate to NGINX status/API."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '80').strip()
    status_path = form_data.get('status_path', '/nginx_status').strip()
    use_https = form_data.get('use_https', False)
    is_plus = form_data.get('is_plus', False)
    api_path = form_data.get('api_path', '/api').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        auth = HTTPBasicAuth(username, password) if username else None
        
        if is_plus:
            # NGINX Plus API
            url = f"{base_url}{api_path}"
            response = requests.get(url, auth=auth, verify=verify_ssl, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Get NGINX info
                nginx_url = f"{base_url}{api_path}/nginx"
                nginx_resp = requests.get(nginx_url, auth=auth, verify=verify_ssl, timeout=10)
                version = 'unknown'
                if nginx_resp.status_code == 200:
                    version = nginx_resp.json().get('version', 'unknown')
                
                return True, f"Successfully connected to NGINX Plus {version}\nAPI endpoints: {data}"
            elif response.status_code == 401:
                return False, "Authentication failed: Unauthorized"
            else:
                return False, f"HTTP {response.status_code}"
        else:
            # Standard NGINX stub_status
            url = f"{base_url}{status_path}"
            response = requests.get(url, auth=auth, verify=verify_ssl, timeout=10)
            
            if response.status_code == 200:
                # Parse stub_status output
                text = response.text
                lines = text.strip().split('\n')
                
                active = 'unknown'
                for line in lines:
                    if 'Active connections' in line:
                        active = line.split(':')[1].strip()
                
                return True, f"Successfully connected to NGINX at {host}:{port}\nActive connections: {active}"
            elif response.status_code == 401:
                return False, "Authentication failed: Unauthorized"
            else:
                return False, f"HTTP {response.status_code}: Status module may not be enabled"
    except Exception as e:
        return False, f"NGINX error: {e}"

