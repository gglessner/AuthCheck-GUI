# Apache Syncope Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Syncope (IAM)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "9080",
     "port_toggle": "use_https", "tls_port": "9443", "non_tls_port": "9080"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "domain", "type": "text", "label": "Domain", "default": "Master"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 9443, Non-TLS: 9080. admin / password"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Syncope.
    """
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    domain = form_data.get('domain', 'Master').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "9080"
        base_url = f"{scheme}://{host}:{port_num}/syncope/rest"
        
        auth = HTTPBasicAuth(username, password)
        headers = {
            "X-Syncope-Domain": domain,
            "Accept": "application/json"
        }
        
        # Get platform info
        url = f"{base_url}/platform"
        response = requests.get(url, auth=auth, headers=headers, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('version', 'unknown')
            
            # Get self info (current user)
            self_url = f"{base_url}/users/self"
            self_response = requests.get(self_url, auth=auth, headers=headers, verify=verify_ssl, timeout=10)
            user_info = "unknown"
            if self_response.status_code == 200:
                self_data = self_response.json()
                user_info = self_data.get('username', username)
            
            # Get user count
            users_url = f"{base_url}/users?page=1&size=1"
            users_response = requests.get(users_url, auth=auth, headers=headers, verify=verify_ssl, timeout=10)
            total_users = 0
            if users_response.status_code == 200:
                total_users = int(users_response.headers.get('X-Total-Count', 0))
            
            return True, f"Successfully authenticated to Apache Syncope {version}\nDomain: {domain}\nUser: {user_info}\nTotal Users: {total_users}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Syncope error: {e}"

