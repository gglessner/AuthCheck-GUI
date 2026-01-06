# Apache Ranger Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Ranger (IAM)"

form_fields = [
    {"name": "host", "type": "text", "label": "Ranger Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "6080",
     "port_toggle": "use_https", "tls_port": "6182", "non_tls_port": "6080"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 6182, Non-TLS: 6080. admin / admin (requires change)"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Ranger.
    """
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Ranger Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "6080"
        base_url = f"{scheme}://{host}:{port_num}"
        
        auth = HTTPBasicAuth(username, password)
        
        # Get user info (validates auth)
        url = f"{base_url}/service/xusers/users"
        response = requests.get(url, auth=auth, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            total_users = data.get('totalCount', 0)
            
            # Get services
            svc_url = f"{base_url}/service/plugins/services"
            svc_response = requests.get(svc_url, auth=auth, verify=verify_ssl, timeout=10)
            services = []
            if svc_response.status_code == 200:
                services = [s.get('name') for s in svc_response.json().get('services', [])]
            
            return True, f"Successfully authenticated to Apache Ranger at {host}:{port_num}\nUsers: {total_users}, Services: {services}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Ranger error: {e}"

