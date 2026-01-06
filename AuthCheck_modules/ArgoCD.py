# ArgoCD Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "ArgoCD (CI/CD)"

form_fields = [
    {"name": "server", "type": "text", "label": "ArgoCD Server"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "token", "type": "password", "label": "Auth Token (Alternative)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / (initial password in argocd-initial-admin-secret). Get with: kubectl -n argocd get secret..."},
]


def authenticate(form_data):
    """Attempt to authenticate to ArgoCD."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    server = form_data.get('server', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    token = form_data.get('token', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not server:
        return False, "ArgoCD Server is required"
    
    if not server.startswith('http'):
        server = f"https://{server}"
    server = server.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        if token:
            headers = {'Authorization': f'Bearer {token}'}
        else:
            if not username:
                return False, "Username or Token is required"
            
            # Login to get token
            login_data = {'username': username, 'password': password}
            login_resp = session.post(f"{server}/api/v1/session",
                                     json=login_data, timeout=15)
            
            if login_resp.status_code == 200:
                token = login_resp.json().get('token')
                headers = {'Authorization': f'Bearer {token}'}
            else:
                return False, f"Login failed: {login_resp.status_code}"
        
        # Get version
        version_resp = session.get(f"{server}/api/version", headers=headers, timeout=10)
        version = 'unknown'
        if version_resp.status_code == 200:
            version = version_resp.json().get('Version', 'unknown')
        
        # Get application count
        apps_resp = session.get(f"{server}/api/v1/applications", headers=headers, timeout=10)
        app_count = 0
        if apps_resp.status_code == 200:
            app_count = len(apps_resp.json().get('items', []))
        
        # Get cluster count
        clusters_resp = session.get(f"{server}/api/v1/clusters", headers=headers, timeout=10)
        cluster_count = 0
        if clusters_resp.status_code == 200:
            cluster_count = len(clusters_resp.json().get('items', []))
        
        # Get repo count
        repos_resp = session.get(f"{server}/api/v1/repositories", headers=headers, timeout=10)
        repo_count = 0
        if repos_resp.status_code == 200:
            repo_count = len(repos_resp.json().get('items', []))
        
        return True, f"Successfully authenticated to ArgoCD {version}\nApplications: {app_count}\nClusters: {cluster_count}\nRepositories: {repo_count}"
        
    except Exception as e:
        return False, f"ArgoCD error: {e}"

