# Oracle WebLogic Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Oracle WebLogic (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Admin Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Admin Port", "default": "7001",
     "port_toggle": "use_https", "tls_port": "7002", "non_tls_port": "7001"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username", "default": "weblogic"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 7002, Non-TLS: 7001. weblogic / welcome1"},
]


def authenticate(form_data):
    """Attempt to authenticate to Oracle WebLogic."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '7001').strip()
    use_https = form_data.get('use_https', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Admin Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        auth = HTTPBasicAuth(username, password)
        headers = {
            'Accept': 'application/json',
            'X-Requested-By': 'authcheck'
        }
        
        # Try REST management API
        url = f"{base_url}/management/weblogic/latest/domainRuntime"
        response = requests.get(url, auth=auth, headers=headers, 
                               verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            domain_name = data.get('name', 'unknown')
            
            # Get servers
            servers_url = f"{base_url}/management/weblogic/latest/domainRuntime/serverRuntimes"
            servers_resp = requests.get(servers_url, auth=auth, headers=headers,
                                       verify=verify_ssl, timeout=10)
            servers = []
            if servers_resp.status_code == 200:
                servers_data = servers_resp.json()
                servers = [s.get('name') for s in servers_data.get('items', [])]
            
            return True, f"Successfully authenticated to WebLogic\nDomain: {domain_name}\nServers: {servers}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 404:
            # Try console login
            console_url = f"{base_url}/console/login/LoginForm.jsp"
            console_resp = requests.get(console_url, verify=verify_ssl, timeout=10)
            if console_resp.status_code == 200:
                return True, f"WebLogic Console accessible at {host}:{port} (REST API may be disabled)"
            return False, "WebLogic REST API not found"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, f"WebLogic error: {e}"

