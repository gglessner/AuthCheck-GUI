# Apache Kylin Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Kylin (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "7070",
     "port_toggle": "use_https", "tls_port": "7443", "non_tls_port": "7070"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username", "default": "ADMIN"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 7443, Non-TLS: 7070. ADMIN / KYLIN"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Kylin.
    """
    try:
        import requests
        import base64
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
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
        port_num = port if port else "7070"
        base_url = f"{scheme}://{host}:{port_num}/kylin/api"
        
        # Kylin uses basic auth with base64 encoding
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json"
        }
        
        # Login
        login_url = f"{base_url}/user/authentication"
        response = requests.post(login_url, headers=headers, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            user_name = user_data.get('userDetails', {}).get('username', username)
            authorities = [a.get('authority') for a in user_data.get('userDetails', {}).get('authorities', [])]
            
            # Get projects
            proj_url = f"{base_url}/projects"
            proj_response = requests.get(proj_url, headers=headers, verify=verify_ssl, timeout=10)
            projects = []
            if proj_response.status_code == 200:
                projects = [p.get('name') for p in proj_response.json()]
            
            return True, f"Successfully authenticated to Apache Kylin\nUser: {user_name}\nRoles: {authorities}\nProjects: {projects}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Kylin error: {e}"

