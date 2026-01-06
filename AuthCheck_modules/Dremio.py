# Dremio Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Dremio (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Dremio Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "9047",
     "port_toggle": "use_ssl", "tls_port": "443", "non_tls_port": "9047"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 443, Non-TLS: 9047. admin / dremio123. Data lakehouse."},
]


def authenticate(form_data):
    """Attempt to authenticate to Dremio."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '9047').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "Dremio Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        scheme = "https" if use_ssl else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        # Login
        login_resp = requests.post(
            f"{base_url}/apiv2/login",
            json={'userName': username, 'password': password},
            timeout=15,
            verify=False
        )
        
        if login_resp.status_code == 200:
            token = login_resp.json().get('token')
            headers = {'Authorization': f'_dremio{token}'}
            
            # Get user info
            user_resp = requests.get(
                f"{base_url}/api/v3/user/by-name/{username}",
                headers=headers,
                timeout=10,
                verify=False
            )
            user_info = ""
            if user_resp.status_code == 200:
                user = user_resp.json()
                email = user.get('email', 'N/A')
                user_info = f"\nEmail: {email}"
            
            # Get sources
            sources_resp = requests.get(
                f"{base_url}/api/v3/catalog",
                headers=headers,
                timeout=10,
                verify=False
            )
            source_count = 0
            if sources_resp.status_code == 200:
                sources = sources_resp.json().get('data', [])
                source_count = len(sources)
            
            return True, f"Successfully authenticated to Dremio\nHost: {host}:{port}\nUser: {username}{user_info}\nCatalog Items: {source_count}"
        elif login_resp.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {login_resp.status_code}: {login_resp.text[:200]}"
            
    except Exception as e:
        return False, f"Dremio error: {e}"

