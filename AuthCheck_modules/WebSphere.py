# IBM WebSphere Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "IBM WebSphere (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "admin_port", "type": "text", "label": "Admin Port", "default": "9043",
     "port_toggle": "use_https", "tls_port": "9043", "non_tls_port": "9060"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "wasadmin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 9043, Non-TLS: 9060. wasadmin / wasadmin"},
]


def authenticate(form_data):
    """Attempt to authenticate to IBM WebSphere."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    admin_port = form_data.get('admin_port', '9043').strip()
    use_https = form_data.get('use_https', True)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{admin_port}"
        
        auth = HTTPBasicAuth(username, password)
        
        # Try REST connector
        url = f"{base_url}/IBMJMXConnectorREST/mbeans"
        headers = {'Accept': 'application/json'}
        
        response = requests.get(url, auth=auth, headers=headers, 
                               verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            mbean_count = len(data) if isinstance(data, list) else 0
            
            return True, f"Successfully authenticated to WebSphere at {host}:{admin_port}\nMBeans: {mbean_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Authentication failed: Access denied"
        else:
            # Try admin console
            console_url = f"{base_url}/ibm/console"
            console_resp = requests.get(console_url, verify=verify_ssl, timeout=10,
                                       allow_redirects=False)
            if console_resp.status_code in [200, 302]:
                return True, f"WebSphere Console accessible at {host}:{admin_port}"
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, f"WebSphere error: {e}"

