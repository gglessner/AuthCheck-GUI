# Exabeam Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Exabeam (Security)"

form_fields = [
    {"name": "url", "type": "text", "label": "Exabeam URL"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: admin/(configured during setup). Uses Advanced Analytics API."},
]


def authenticate(form_data):
    """Attempt to authenticate to Exabeam."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not url:
        return False, "Exabeam URL is required"
    if not username:
        return False, "Username is required"
    
    if not url.startswith('http'):
        url = f"https://{url}"
    url = url.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # Login
        login_resp = session.post(
            f"{url}/api/auth/login",
            json={'username': username, 'password': password},
            timeout=15
        )
        
        if login_resp.status_code == 200:
            # Get session info
            me_resp = session.get(f"{url}/api/auth/me", timeout=10)
            user_info = {}
            if me_resp.status_code == 200:
                user_info = me_resp.json()
            
            user = user_info.get('username', username)
            role = user_info.get('role', 'unknown')
            
            # Get cluster info
            cluster_resp = session.get(f"{url}/api/admin/cluster/status", timeout=10)
            cluster_info = ""
            if cluster_resp.status_code == 200:
                cluster = cluster_resp.json()
                nodes = len(cluster.get('nodes', []))
                cluster_info = f"\nCluster Nodes: {nodes}"
            
            return True, f"Successfully authenticated to Exabeam\nUser: {user}\nRole: {role}{cluster_info}"
        elif login_resp.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {login_resp.status_code}: {login_resp.text[:200]}"
            
    except Exception as e:
        return False, f"Exabeam error: {e}"

