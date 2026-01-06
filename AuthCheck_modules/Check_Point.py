# Check Point Security Gateway Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Check Point Security Gateway (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "Management Server"},
    {"name": "port", "type": "text", "label": "API Port", "default": "443",
     "port_toggle": "verify_ssl", "tls_port": "443", "non_tls_port": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "api_key", "type": "password", "label": "API Key (Alternative)"},
    {"name": "domain", "type": "text", "label": "Domain (MDS)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 443 (always TLS). admin / (set during setup). Web API must be enabled."},
]


def authenticate(form_data):
    """Attempt to authenticate to Check Point Management Server."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
    username = form_data.get('username', 'admin').strip()
    password = form_data.get('password', '')
    api_key = form_data.get('api_key', '').strip()
    domain = form_data.get('domain', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Management Server is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        headers = {'Content-Type': 'application/json'}
        
        # Login
        login_data = {}
        if api_key:
            login_data['api-key'] = api_key
        else:
            if not username:
                return False, "Username or API Key is required"
            login_data['user'] = username
            login_data['password'] = password
        
        if domain:
            login_data['domain'] = domain
        
        response = session.post(f"{host}:{port}/web_api/login",
                               json=login_data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'sid' in data:
                sid = data['sid']
                
                # Get session info
                api_version = data.get('api-server-version', 'unknown')
                session_timeout = data.get('session-timeout', 'unknown')
                
                # Get gateways
                headers['X-chkp-sid'] = sid
                gw_resp = session.post(f"{host}:{port}/web_api/show-gateways-and-servers",
                                      json={'limit': 50}, headers=headers, timeout=15)
                gw_count = 0
                if gw_resp.status_code == 200:
                    gw_count = gw_resp.json().get('total', 0)
                
                # Get policy packages
                pkg_resp = session.post(f"{host}:{port}/web_api/show-packages",
                                       json={}, headers=headers, timeout=15)
                pkg_count = 0
                if pkg_resp.status_code == 200:
                    pkg_count = pkg_resp.json().get('total', 0)
                
                # Logout
                session.post(f"{host}:{port}/web_api/logout",
                            json={}, headers=headers, timeout=5)
                
                return True, f"Successfully authenticated to Check Point\nAPI Version: {api_version}\nGateways/Servers: {gw_count}\nPolicy Packages: {pkg_count}"
            else:
                return False, f"Login failed: {data.get('message', 'Unknown error')}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('message', response.text[:200])
            except:
                error_msg = response.text[:200]
            return False, f"Authentication failed: {error_msg}"
            
    except Exception as e:
        return False, f"Check Point error: {e}"

