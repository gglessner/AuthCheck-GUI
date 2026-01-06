# Veritas NetBackup Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Veritas NetBackup (Backup)"

form_fields = [
    {"name": "host", "type": "text", "label": "Master Server"},
    {"name": "port", "type": "text", "label": "API Port", "default": "1556"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "domain_name", "type": "text", "label": "Domain Name"},
    {"name": "domain_type", "type": "combo", "label": "Domain Type", "options": ["unixpwd", "vx", "nt", "ldap"], "default": "unixpwd"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Master server hostname. Domain types: unixpwd (Unix), vx (VxSS), nt (Windows), ldap."},
]


def authenticate(form_data):
    """Attempt to authenticate to Veritas NetBackup."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '1556').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    domain_name = form_data.get('domain_name', '').strip()
    domain_type = form_data.get('domain_type', 'unixpwd')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Master Server is required"
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
            'userName': username,
            'password': password,
            'domainType': domain_type
        }
        
        if domain_name:
            login_data['domainName'] = domain_name
        
        headers = {'Content-Type': 'application/vnd.netbackup+json;version=4.0'}
        
        response = session.post(f"{host}:{port}/netbackup/login",
                               json=login_data, headers=headers, timeout=15)
        
        if response.status_code == 201:
            token = response.json().get('token')
            
            headers['Authorization'] = token
            
            # Get server info
            ping_resp = session.get(f"{host}:{port}/netbackup/ping",
                                   headers=headers, timeout=10)
            version = 'unknown'
            if ping_resp.status_code == 200:
                version = ping_resp.json().get('version', 'unknown')
            
            # Get client count
            clients_resp = session.get(f"{host}:{port}/netbackup/config/clients",
                                      headers=headers, timeout=10)
            client_count = 0
            if clients_resp.status_code == 200:
                client_count = len(clients_resp.json().get('data', []))
            
            # Get policy count
            policies_resp = session.get(f"{host}:{port}/netbackup/config/policies",
                                       headers=headers, timeout=10)
            policy_count = 0
            if policies_resp.status_code == 200:
                policy_count = len(policies_resp.json().get('data', []))
            
            # Logout
            session.post(f"{host}:{port}/netbackup/logout", headers=headers, timeout=5)
            
            return True, f"Successfully authenticated to NetBackup {version}\nMaster: {host}\nClients: {client_count}\nPolicies: {policy_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"NetBackup error: {e}"

