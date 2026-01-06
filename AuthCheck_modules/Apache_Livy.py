# Apache Livy Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Livy (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Livy Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8998",
     "port_toggle": "use_https", "tls_port": "8998", "non_tls_port": "8998"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Basic Auth", "Kerberos"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 8998 (TLS/non-TLS same). livy / livy"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Livy.
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
        return False, "Livy Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "8998"
        base_url = f"{scheme}://{host}:{port_num}"
        
        auth = None
        if auth_type == "Basic Auth" and username:
            auth = HTTPBasicAuth(username, password)
        
        # Get Livy sessions
        url = f"{base_url}/sessions"
        response = requests.get(url, auth=auth, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            sessions = data.get('sessions', [])
            total = data.get('total', len(sessions))
            
            # Get batches
            batch_url = f"{base_url}/batches"
            batch_response = requests.get(batch_url, auth=auth, verify=verify_ssl, timeout=10)
            batches = 0
            if batch_response.status_code == 200:
                batches = batch_response.json().get('total', 0)
            
            return True, f"Successfully connected to Apache Livy at {host}:{port_num}\nSessions: {total}, Batches: {batches}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Livy error: {e}"

