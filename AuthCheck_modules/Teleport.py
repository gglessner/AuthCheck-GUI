# Teleport Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Teleport (IAM)"

form_fields = [
    {"name": "proxy_addr", "type": "text", "label": "Proxy Address"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "token", "type": "password", "label": "API Token (Alternative)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Proxy Address: teleport.example.com:443. API token from tctl tokens add."},
]


def authenticate(form_data):
    """Attempt to authenticate to Teleport."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    proxy_addr = form_data.get('proxy_addr', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    token = form_data.get('token', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not proxy_addr:
        return False, "Proxy Address is required"
    
    if not proxy_addr.startswith('http'):
        proxy_addr = f"https://{proxy_addr}"
    proxy_addr = proxy_addr.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        if token:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Get cluster info via API
            response = session.get(f"{proxy_addr}/v1/webapi/ping",
                                  headers=headers, timeout=15)
        else:
            if not username:
                return False, "Username or Token required"
            
            # Web login
            login_data = {
                'user': username,
                'pass': password,
                'second_factor_token': ''
            }
            
            response = session.post(f"{proxy_addr}/v1/webapi/sessions/web",
                                   json=login_data, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Get ping info for cluster details
            ping_resp = session.get(f"{proxy_addr}/v1/webapi/ping", timeout=10)
            cluster_name = 'unknown'
            version = 'unknown'
            if ping_resp.status_code == 200:
                ping_data = ping_resp.json()
                cluster_name = ping_data.get('cluster_name', 'unknown')
                version = ping_data.get('server_version', 'unknown')
            
            return True, f"Successfully authenticated to Teleport {version}\nCluster: {cluster_name}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Authentication failed: Access denied (MFA required?)"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Teleport error: {e}"

