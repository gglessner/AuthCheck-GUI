# CouchDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "CouchDB (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "5984",
     "port_toggle": "use_https", "tls_port": "6984", "non_tls_port": "5984"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 6984, Non-TLS: 5984. admin / admin (set during setup)"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to CouchDB.
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
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "5984"
        base_url = f"{scheme}://{host}:{port_num}"
        
        auth = HTTPBasicAuth(username, password) if username else None
        
        # Get server info
        response = requests.get(base_url, auth=auth, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('version', 'unknown')
            
            # Try to access _session for auth verification
            session_url = f"{base_url}/_session"
            session_response = requests.get(session_url, auth=auth, verify=verify_ssl, timeout=10)
            
            if session_response.status_code == 200:
                session_data = session_response.json()
                user_ctx = session_data.get('userCtx', {})
                auth_user = user_ctx.get('name', 'anonymous')
                roles = user_ctx.get('roles', [])
                
                return True, f"Successfully authenticated to CouchDB {version}\nUser: {auth_user}\nRoles: {roles}"
            else:
                return True, f"Connected to CouchDB {version} (auth status unclear)"
                
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"CouchDB error: {e}"

