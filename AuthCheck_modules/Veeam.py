# Veeam Backup & Replication Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Veeam Backup & Replication (Backup)"

form_fields = [
    {"name": "host", "type": "text", "label": "Veeam Server"},
    {"name": "port", "type": "text", "label": "API Port", "default": "9419"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Windows domain or local account. REST API on port 9419 (v11+)."},
]


def authenticate(form_data):
    """Attempt to authenticate to Veeam Backup & Replication."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '9419').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Veeam Server is required"
    if not username:
        return False, "Username is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # Get access token
        auth_url = f"{host}:{port}/api/oauth2/token"
        auth_data = {
            'grant_type': 'password',
            'username': username,
            'password': password
        }
        
        auth_resp = session.post(auth_url, data=auth_data, timeout=10)
        
        if auth_resp.status_code == 200:
            token_data = auth_resp.json()
            access_token = token_data.get('access_token')
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'x-api-version': '1.1-rev1'
            }
            
            # Get server info
            server_resp = session.get(f"{host}:{port}/api/v1/serverInfo",
                                     headers=headers, timeout=10)
            version = 'unknown'
            server_name = 'unknown'
            if server_resp.status_code == 200:
                server_data = server_resp.json()
                version = server_data.get('databaseVersion', 'unknown')
                server_name = server_data.get('name', 'unknown')
            
            # Get job count
            jobs_resp = session.get(f"{host}:{port}/api/v1/jobs",
                                   headers=headers, timeout=10)
            job_count = 0
            if jobs_resp.status_code == 200:
                jobs = jobs_resp.json()
                job_count = len(jobs.get('data', []))
            
            # Get repository count
            repo_resp = session.get(f"{host}:{port}/api/v1/backupInfrastructure/repositories",
                                   headers=headers, timeout=10)
            repo_count = 0
            if repo_resp.status_code == 200:
                repos = repo_resp.json()
                repo_count = len(repos.get('data', []))
            
            return True, f"Successfully authenticated to Veeam\nServer: {server_name}\nVersion: {version}\nJobs: {job_count}\nRepositories: {repo_count}"
        elif auth_resp.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif auth_resp.status_code == 400:
            return False, "Authentication failed: Bad request - check username format"
        else:
            return False, f"HTTP {auth_resp.status_code}: {auth_resp.text[:200]}"
            
    except Exception as e:
        return False, f"Veeam error: {e}"

