# Apache OpenWhisk Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache OpenWhisk (Cloud)"

form_fields = [
    {"name": "host", "type": "text", "label": "API Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "namespace", "type": "text", "label": "Namespace", "default": "guest"},
    {"name": "auth_key", "type": "password", "label": "Auth Key (user:pass)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 443, Non-TLS: 80. guest / guest"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache OpenWhisk.
    """
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', True)
    namespace = form_data.get('namespace', 'guest').strip()
    auth_key = form_data.get('auth_key', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "API Host is required"
    if not auth_key:
        return False, "Auth Key is required (format: user:password)"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "443"
        base_url = f"{scheme}://{host}:{port_num}/api/v1"
        
        # Parse auth key
        if ':' in auth_key:
            username, password = auth_key.split(':', 1)
        else:
            return False, "Auth Key must be in format user:password"
        
        auth = HTTPBasicAuth(username, password)
        
        # Get namespace info
        url = f"{base_url}/namespaces/{namespace}"
        response = requests.get(url, auth=auth, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            # Get actions
            actions_url = f"{base_url}/namespaces/{namespace}/actions"
            actions_response = requests.get(actions_url, auth=auth, verify=verify_ssl, timeout=10)
            actions = []
            if actions_response.status_code == 200:
                actions = [a.get('name') for a in actions_response.json()]
            
            # Get packages
            packages_url = f"{base_url}/namespaces/{namespace}/packages"
            packages_response = requests.get(packages_url, auth=auth, verify=verify_ssl, timeout=10)
            packages = []
            if packages_response.status_code == 200:
                packages = [p.get('name') for p in packages_response.json()]
            
            return True, f"Successfully authenticated to Apache OpenWhisk\nNamespace: {namespace}\nActions: {len(actions)}, Packages: {len(packages)}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid auth key"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"OpenWhisk error: {e}"

