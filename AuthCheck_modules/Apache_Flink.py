# Apache Flink Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Flink (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "JobManager Host", "default": "localhost"},
    {"name": "rest_port", "type": "text", "label": "REST API Port", "default": "8081",
     "port_toggle": "use_https", "tls_port": "8081", "non_tls_port": "8081"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Basic Auth", "Kerberos"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "ssl_ca", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "REST: 8081 (TLS/non-TLS same). Default: no auth. admin / admin"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Flink REST API.
    """
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    rest_port = form_data.get('rest_port', '').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    ssl_ca = form_data.get('ssl_ca', '').strip()
    
    if not host:
        return False, "JobManager Host is required"
    if not rest_port:
        return False, "REST API Port is required"
    
    try:
        scheme = "https" if use_https else "http"
        url = f"{scheme}://{host}:{rest_port}/overview"
        
        auth = None
        if auth_type == "Basic Auth" and username:
            auth = HTTPBasicAuth(username, password)
        
        verify = ssl_ca if ssl_ca else (not use_https)
        
        response = requests.get(url, auth=auth, timeout=10, verify=verify)
        
        if response.status_code == 200:
            data = response.json()
            flink_version = data.get('flink-version', 'unknown')
            taskmanagers = data.get('taskmanagers', 0)
            slots_total = data.get('slots-total', 0)
            
            return True, f"Successfully connected to Apache Flink {flink_version}\nTaskManagers: {taskmanagers}, Slots: {slots_total}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except requests.exceptions.SSLError as e:
        return False, f"SSL error: {e}"
    except requests.exceptions.ConnectionError as e:
        return False, f"Connection error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

