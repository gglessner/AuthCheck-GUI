# Caddy Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Caddy (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "admin_port", "type": "text", "label": "Admin API Port", "default": "2019"},
    {"name": "http_port", "type": "text", "label": "HTTP Port", "default": "80",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "protocol", "type": "combo", "label": "Protocol",
     "options": ["Admin API", "HTTP/HTTPS"]},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "admin_password", "type": "password", "label": "Admin Password (if configured)"},
    {"name": "basic_user", "type": "text", "label": "Basic Auth Username"},
    {"name": "basic_pass", "type": "password", "label": "Basic Auth Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Admin API: 2019, HTTP: 80, HTTPS: 443. Admin API default: no auth"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Caddy.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    admin_port = form_data.get('admin_port', '').strip()
    http_port = form_data.get('http_port', '').strip()
    protocol = form_data.get('protocol', 'Admin API')
    use_https = form_data.get('use_https', False)
    admin_password = form_data.get('admin_password', '').strip()
    basic_user = form_data.get('basic_user', '').strip()
    basic_pass = form_data.get('basic_pass', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        if protocol == "Admin API":
            url = f"http://{host}:{admin_port}/config/"
            headers = {}
            if admin_password:
                headers['Authorization'] = f"Bearer {admin_password}"
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return True, f"Successfully connected to Caddy Admin API at {host}:{admin_port}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid admin credentials"
            else:
                return False, f"Admin API returned status {response.status_code}"
        else:
            scheme = "https" if use_https else "http"
            url = f"{scheme}://{host}:{http_port}/"
            
            auth = None
            if basic_user:
                auth = (basic_user, basic_pass)
            
            response = requests.get(url, auth=auth, verify=verify_ssl, timeout=10)
            
            server = response.headers.get('Server', '')
            if 'Caddy' in server:
                return True, f"Successfully connected to Caddy at {url}\nServer: {server}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            elif response.status_code < 400:
                return True, f"Successfully connected to {url} (Server: {server or 'unknown'})"
            else:
                return False, f"HTTP returned status {response.status_code}"
                
    except Exception as e:
        return False, f"Error: {e}"

