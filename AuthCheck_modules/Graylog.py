# Graylog Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Graylog (Logging)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "9000",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "9000"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["Basic Auth", "API Token", "Session"]},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password/Token"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 443, Non-TLS: 9000. admin / admin"},
]


def authenticate(form_data):
    """Attempt to authenticate to Graylog."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '9000').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'Basic Auth')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{port}/api"
        
        headers = {'Accept': 'application/json'}
        auth = None
        
        if auth_type == "Basic Auth":
            auth = HTTPBasicAuth(username, password)
        elif auth_type == "API Token":
            auth = HTTPBasicAuth(password, 'token')
        elif auth_type == "Session":
            # Create session
            session_url = f"{base_url}/system/sessions"
            session_data = {"username": username, "password": password}
            session_resp = requests.post(session_url, json=session_data, 
                                        headers=headers, verify=verify_ssl, timeout=10)
            if session_resp.status_code == 200:
                session = session_resp.json()
                headers['X-Graylog-Session-Token'] = session.get('session_id')
            else:
                return False, "Session creation failed"
        
        # Get system info
        response = requests.get(f"{base_url}/system", auth=auth, headers=headers,
                               verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('version', 'unknown')
            cluster_id = data.get('cluster_id', 'unknown')
            node_id = data.get('node_id', 'unknown')
            
            # Get inputs count
            inputs_resp = requests.get(f"{base_url}/system/inputs", auth=auth,
                                      headers=headers, verify=verify_ssl, timeout=10)
            inputs = 0
            if inputs_resp.status_code == 200:
                inputs = inputs_resp.json().get('total', 0)
            
            return True, f"Successfully authenticated to Graylog {version}\nCluster: {cluster_id}\nInputs: {inputs}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, f"Graylog error: {e}"

