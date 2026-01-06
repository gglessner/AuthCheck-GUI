# Apache Guacamole Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Guacamole (IAM)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "context_path", "type": "text", "label": "Context Path", "default": "/guacamole"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username", "default": "guacadmin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8443, Non-TLS: 8080. guacadmin / guacadmin"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Guacamole.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    context_path = form_data.get('context_path', '/guacamole').strip()
    use_https = form_data.get('use_https', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "8080"
        base_url = f"{scheme}://{host}:{port_num}{context_path}/api"
        
        # Get authentication token
        login_url = f"{base_url}/tokens"
        login_data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(login_url, data=login_data, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('authToken')
            auth_user = data.get('username', username)
            data_source = data.get('dataSource', 'unknown')
            
            # Get connections
            headers = {"Guacamole-Token": token}
            conn_url = f"{base_url}/session/data/{data_source}/connections"
            conn_response = requests.get(conn_url, headers=headers, verify=verify_ssl, timeout=10)
            connections = 0
            if conn_response.status_code == 200:
                connections = len(conn_response.json())
            
            # Logout
            requests.delete(f"{base_url}/tokens/{token}", headers=headers, verify=verify_ssl, timeout=5)
            
            return True, f"Successfully authenticated to Apache Guacamole\nUser: {auth_user}\nData Source: {data_source}\nConnections: {connections}"
        elif response.status_code == 403:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Guacamole error: {e}"

