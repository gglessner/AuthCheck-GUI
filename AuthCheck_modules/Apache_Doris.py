# Apache Doris Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Doris (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "FE Host", "default": "localhost"},
    {"name": "http_port", "type": "text", "label": "HTTP Port", "default": "8030"},
    {"name": "query_port", "type": "text", "label": "Query Port", "default": "9030"},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "database", "type": "text", "label": "Database"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "root / (empty), admin / admin"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Doris.
    """
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    http_port = form_data.get('http_port', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    if not host:
        return False, "FE Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        port_num = http_port if http_port else "8030"
        base_url = f"http://{host}:{port_num}/api"
        
        auth = HTTPBasicAuth(username, password)
        
        # Get cluster info via bootstrap
        url = f"{base_url}/bootstrap"
        response = requests.get(url, auth=auth, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Get backends
            be_url = f"http://{host}:{port_num}/rest/v1/system?path=/backends"
            be_response = requests.get(be_url, auth=auth, timeout=10)
            backends = 0
            if be_response.status_code == 200:
                be_data = be_response.json()
                backends = len(be_data.get('data', {}).get('rows', []))
            
            # Get frontends
            fe_url = f"http://{host}:{port_num}/rest/v1/system?path=/frontends"
            fe_response = requests.get(fe_url, auth=auth, timeout=10)
            frontends = 0
            if fe_response.status_code == 200:
                fe_data = fe_response.json()
                frontends = len(fe_data.get('data', {}).get('rows', []))
            
            return True, f"Successfully authenticated to Apache Doris at {host}:{port_num}\nFrontends: {frontends}, Backends: {backends}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Doris error: {e}"

