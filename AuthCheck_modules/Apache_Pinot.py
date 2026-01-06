# Apache Pinot Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Pinot (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Controller Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Controller Port", "default": "9000",
     "port_toggle": "use_https", "tls_port": "9000", "non_tls_port": "9000"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Basic Auth", "Token"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password/Token"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Controller: 9000 (TLS/non-TLS same). admin / admin"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Pinot.
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
        return False, "Controller Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "9000"
        base_url = f"{scheme}://{host}:{port_num}"
        
        auth = None
        headers = {}
        if auth_type == "Basic Auth" and username:
            auth = HTTPBasicAuth(username, password)
        elif auth_type == "Token" and password:
            headers['Authorization'] = f"Bearer {password}"
        
        # Get cluster info
        url = f"{base_url}/cluster/info"
        response = requests.get(url, auth=auth, headers=headers, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            cluster_name = data.get('clusterName', 'unknown')
            
            # Get tables
            tables_url = f"{base_url}/tables"
            tables_response = requests.get(tables_url, auth=auth, headers=headers, verify=verify_ssl, timeout=10)
            tables = []
            if tables_response.status_code == 200:
                tables = tables_response.json().get('tables', [])
            
            # Get brokers
            brokers_url = f"{base_url}/brokers/tenants"
            brokers_response = requests.get(brokers_url, auth=auth, headers=headers, verify=verify_ssl, timeout=10)
            brokers = 0
            if brokers_response.status_code == 200:
                brokers = len(brokers_response.json())
            
            return True, f"Successfully connected to Apache Pinot\nCluster: {cluster_name}\nTables: {len(tables)}, Brokers: {brokers}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Pinot error: {e}"

