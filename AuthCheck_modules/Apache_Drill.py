# Apache Drill Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Drill (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Drillbit Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Web UI Port", "default": "8047",
     "port_toggle": "use_https", "tls_port": "8047", "non_tls_port": "8047"},
    {"name": "user_port", "type": "text", "label": "User Port", "default": "31010"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Plain", "Kerberos", "MapR-SASL"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Web: 8047, User: 31010 (TLS/non-TLS same). admin / admin"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Drill.
    """
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Drillbit Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "8047"
        base_url = f"{scheme}://{host}:{port_num}"
        
        session = requests.Session()
        
        # Handle authentication
        if auth_type == "Plain" and username:
            # Drill form-based login
            login_url = f"{base_url}/j_security_check"
            login_data = {
                "j_username": username,
                "j_password": password
            }
            login_response = session.post(login_url, data=login_data, verify=verify_ssl, timeout=10)
        
        # Get cluster info
        url = f"{base_url}/cluster.json"
        response = session.get(url, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            drillbits = data.get('drillbits', [])
            current = data.get('currentVersion', 'unknown')
            
            nodes = []
            for bit in drillbits:
                addr = bit.get('address', 'unknown')
                state = bit.get('state', 'unknown')
                nodes.append(f"{addr}({state})")
            
            # Get storage plugins
            storage_url = f"{base_url}/storage.json"
            storage_response = session.get(storage_url, verify=verify_ssl, timeout=10)
            plugins = []
            if storage_response.status_code == 200:
                plugins = [p.get('name') for p in storage_response.json() if p.get('enabled', False)]
            
            return True, f"Successfully connected to Apache Drill {current}\nDrillbits: {', '.join(nodes)}\nEnabled Plugins: {plugins}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Drill error: {e}"

