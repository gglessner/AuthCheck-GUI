# Rubrik Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Rubrik (Backup)"

form_fields = [
    {"name": "host", "type": "text", "label": "Rubrik Cluster"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "api_token", "type": "password", "label": "API Token (Alternative)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / (set during bootstrap). API token from Settings > API Token Management."},
]


def authenticate(form_data):
    """Attempt to authenticate to Rubrik."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    api_token = form_data.get('api_token', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Rubrik Cluster is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        if api_token:
            headers = {'Authorization': f'Bearer {api_token}'}
        else:
            if not username:
                return False, "Username or API Token is required"
            # Get API token using basic auth
            auth = HTTPBasicAuth(username, password)
            token_resp = session.post(f"{host}/api/v1/session",
                                     auth=auth, timeout=15)
            
            if token_resp.status_code == 200:
                api_token = token_resp.json().get('token')
                headers = {'Authorization': f'Bearer {api_token}'}
            else:
                return False, f"Authentication failed: {token_resp.status_code}"
        
        # Get cluster info
        response = session.get(f"{host}/api/v1/cluster/me",
                              headers=headers, timeout=15)
        
        if response.status_code == 200:
            cluster = response.json()
            cluster_name = cluster.get('name', 'unknown')
            version = cluster.get('version', 'unknown')
            
            # Get node count
            nodes_resp = session.get(f"{host}/api/internal/cluster/me/node",
                                    headers=headers, timeout=10)
            node_count = 0
            if nodes_resp.status_code == 200:
                node_count = len(nodes_resp.json().get('data', []))
            
            # Get SLA domain count
            sla_resp = session.get(f"{host}/api/v2/sla_domain",
                                  headers=headers, timeout=10)
            sla_count = 0
            if sla_resp.status_code == 200:
                sla_count = sla_resp.json().get('total', 0)
            
            return True, f"Successfully authenticated to Rubrik {version}\nCluster: {cluster_name}\nNodes: {node_count}\nSLA Domains: {sla_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Rubrik error: {e}"

