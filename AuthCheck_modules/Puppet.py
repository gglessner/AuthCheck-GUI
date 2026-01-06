# Puppet Enterprise Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Puppet Enterprise (CI/CD)"

form_fields = [
    {"name": "host", "type": "text", "label": "Puppet Server"},
    {"name": "port", "type": "text", "label": "Console Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "token", "type": "password", "label": "RBAC Token (Alternative)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / (set at install). Token from puppet access login or Console."},
]


def authenticate(form_data):
    """Attempt to authenticate to Puppet Enterprise."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    token = form_data.get('token', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Puppet Server is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        if token:
            headers = {'X-Authentication': token}
        else:
            if not username:
                return False, "Username or Token required"
            
            # Get auth token
            auth_resp = session.post(
                f"{host}:{port}/rbac-api/v1/auth/token",
                json={'login': username, 'password': password},
                timeout=15
            )
            
            if auth_resp.status_code == 200:
                token = auth_resp.json().get('token')
                headers = {'X-Authentication': token}
            else:
                return False, f"Login failed: {auth_resp.status_code}"
        
        # Get status
        response = session.get(f"{host}:{port}/status/v1/services",
                              headers=headers, timeout=15)
        
        if response.status_code == 200:
            services = response.json()
            
            # Get node count
            nodes_resp = session.get(f"{host}:{port}/pdb/query/v4/nodes",
                                    headers=headers, timeout=10)
            node_count = 0
            if nodes_resp.status_code == 200:
                node_count = len(nodes_resp.json())
            
            # Get environment count
            envs_resp = session.get(f"{host}:{port}/classifier-api/v1/environments",
                                   headers=headers, timeout=10)
            env_count = 0
            if envs_resp.status_code == 200:
                env_count = len(envs_resp.json())
            
            service_count = len(services) if isinstance(services, dict) else 0
            
            return True, f"Successfully authenticated to Puppet Enterprise\nServices: {service_count}\nNodes: {node_count}\nEnvironments: {env_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Puppet error: {e}"

