# Cohesity Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Cohesity (Backup)"

form_fields = [
    {"name": "host", "type": "text", "label": "Cluster VIP"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "domain", "type": "text", "label": "Domain", "default": "LOCAL"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / (set during setup). Domain: LOCAL for local users, AD domain for AD users."},
]


def authenticate(form_data):
    """Attempt to authenticate to Cohesity."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    domain = form_data.get('domain', 'LOCAL').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Cluster VIP is required"
    if not username:
        return False, "Username is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # Login
        login_data = {
            'username': username,
            'password': password,
            'domain': domain
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = session.post(f"{host}/irisservices/api/v1/public/accessTokens",
                               json=login_data, headers=headers, timeout=15)
        
        if response.status_code in [200, 201]:
            token_data = response.json()
            access_token = token_data.get('accessToken')
            
            headers['Authorization'] = f'Bearer {access_token}'
            
            # Get cluster info
            cluster_resp = session.get(f"{host}/irisservices/api/v1/public/cluster",
                                      headers=headers, timeout=10)
            cluster_name = 'unknown'
            version = 'unknown'
            if cluster_resp.status_code == 200:
                cluster = cluster_resp.json()
                cluster_name = cluster.get('name', 'unknown')
                version = cluster.get('clusterSoftwareVersion', 'unknown')
            
            # Get node count
            nodes_resp = session.get(f"{host}/irisservices/api/v1/public/nodes",
                                    headers=headers, timeout=10)
            node_count = 0
            if nodes_resp.status_code == 200:
                node_count = len(nodes_resp.json())
            
            # Get protection job count
            jobs_resp = session.get(f"{host}/irisservices/api/v1/public/protectionJobs",
                                   headers=headers, timeout=10)
            job_count = 0
            if jobs_resp.status_code == 200:
                job_count = len(jobs_resp.json())
            
            return True, f"Successfully authenticated to Cohesity {version}\nCluster: {cluster_name}\nNodes: {node_count}\nProtection Jobs: {job_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Cohesity error: {e}"

