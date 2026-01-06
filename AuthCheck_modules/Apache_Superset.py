# Apache Superset Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Superset (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8088",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "8088"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "provider", "type": "combo", "label": "Auth Provider",
     "options": ["Database", "LDAP", "OAuth"]},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 443, Non-TLS: 8088. admin / admin (fab create-admin)"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Superset.
    """
    try:
        import requests
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
        port_num = port if port else "8088"
        base_url = f"{scheme}://{host}:{port_num}"
        
        session = requests.Session()
        
        # Get CSRF token
        login_page = session.get(f"{base_url}/login/", verify=verify_ssl, timeout=10)
        
        # Try API login
        login_url = f"{base_url}/api/v1/security/login"
        login_data = {
            "username": username,
            "password": password,
            "provider": "db",
            "refresh": True
        }
        
        response = session.post(login_url, json=login_data, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            
            if access_token:
                # Get current user info
                headers = {"Authorization": f"Bearer {access_token}"}
                me_url = f"{base_url}/api/v1/me/"
                me_response = session.get(me_url, headers=headers, verify=verify_ssl, timeout=10)
                
                if me_response.status_code == 200:
                    user_data = me_response.json().get('result', {})
                    user_name = user_data.get('username', username)
                    roles = [r.get('name') for r in user_data.get('roles', [])]
                    
                    return True, f"Successfully authenticated to Apache Superset\nUser: {user_name}\nRoles: {roles}"
            
            return True, f"Successfully authenticated to Apache Superset as {username}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Superset error: {e}"

