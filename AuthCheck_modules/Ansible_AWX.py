# Ansible AWX/Tower Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Ansible AWX/Tower (CI/CD)"

form_fields = [
    {"name": "host", "type": "text", "label": "AWX/Tower Host"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "token", "type": "password", "label": "API Token (Alternative)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / password (AWX default). Tower: admin / (set during install). API token from User > Tokens."},
]


def authenticate(form_data):
    """Attempt to authenticate to Ansible AWX/Tower."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    username = form_data.get('username', 'admin').strip()
    password = form_data.get('password', '')
    token = form_data.get('token', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "AWX/Tower Host is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
            response = session.get(f"{host}/api/v2/me/",
                                  headers=headers, timeout=15)
        else:
            if not username:
                return False, "Username or Token is required"
            response = session.get(f"{host}/api/v2/me/",
                                  auth=(username, password),
                                  headers=headers, timeout=15)
        
        if response.status_code == 200:
            user_data = response.json()
            user_name = user_data.get('username', 'unknown')
            is_superuser = user_data.get('is_superuser', False)
            
            # Get version
            config_resp = session.get(f"{host}/api/v2/config/",
                                     headers=headers,
                                     auth=None if token else (username, password),
                                     timeout=10)
            version = 'unknown'
            product = 'AWX'
            if config_resp.status_code == 200:
                config_data = config_resp.json()
                version = config_data.get('version', 'unknown')
                if 'tower' in config_data.get('license_info', {}).get('license_type', '').lower():
                    product = 'Ansible Tower'
            
            # Get job template count
            jt_resp = session.get(f"{host}/api/v2/job_templates/",
                                 headers=headers,
                                 auth=None if token else (username, password),
                                 timeout=10)
            jt_count = 0
            if jt_resp.status_code == 200:
                jt_count = jt_resp.json().get('count', 0)
            
            # Get inventory count
            inv_resp = session.get(f"{host}/api/v2/inventories/",
                                  headers=headers,
                                  auth=None if token else (username, password),
                                  timeout=10)
            inv_count = 0
            if inv_resp.status_code == 200:
                inv_count = inv_resp.json().get('count', 0)
            
            return True, f"Successfully authenticated to {product} {version}\nUser: {user_name}\nSuperuser: {is_superuser}\nJob Templates: {jt_count}\nInventories: {inv_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"AWX/Tower error: {e}"

