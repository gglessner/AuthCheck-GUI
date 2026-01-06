# Apache Knox Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Knox Gateway (IAM)"

form_fields = [
    {"name": "host", "type": "text", "label": "Knox Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8443"},
    {"name": "topology", "type": "text", "label": "Topology", "default": "default"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "ssl_ca", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / admin-password, guest / guest-password"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Knox Gateway.
    """
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    topology = form_data.get('topology', 'default').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    ssl_ca = form_data.get('ssl_ca', '').strip()
    
    if not host:
        return False, "Knox Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        port_num = port if port else "8443"
        base_url = f"https://{host}:{port_num}/gateway/{topology}"
        
        auth = HTTPBasicAuth(username, password)
        verify = ssl_ca if ssl_ca else verify_ssl
        
        # Try to access WebHDFS through Knox
        url = f"{base_url}/webhdfs/v1/?op=LISTSTATUS"
        response = requests.get(url, auth=auth, verify=verify, timeout=10)
        
        if response.status_code == 200:
            return True, f"Successfully authenticated to Apache Knox at {host}:{port_num}\nTopology: {topology}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        elif response.status_code == 404:
            # Try admin API
            admin_url = f"https://{host}:{port_num}/gateway/admin/api/v1/version"
            admin_response = requests.get(admin_url, auth=auth, verify=verify, timeout=10)
            if admin_response.status_code == 200:
                version = admin_response.json().get('version', 'unknown')
                return True, f"Successfully authenticated to Apache Knox {version}\nAdmin API accessible"
            return False, f"Topology '{topology}' not found or service unavailable"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Knox error: {e}"

