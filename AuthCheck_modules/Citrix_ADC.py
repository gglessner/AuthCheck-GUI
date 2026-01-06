# Citrix ADC (NetScaler) Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Citrix ADC / NetScaler (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "ADC Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "username", "type": "text", "label": "Username", "default": "nsroot"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "HTTPS: 443, HTTP: 80. nsroot / nsroot (default)."},
]


def authenticate(form_data):
    """Attempt to authenticate to Citrix ADC (NetScaler)."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    username = form_data.get('username', 'nsroot').strip()
    password = form_data.get('password', '')
    use_https = form_data.get('use_https', True)
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "ADC Host is required"
    if not username:
        return False, "Username is required"
    
    scheme = "https" if use_https else "http"
    if not host.startswith('http'):
        host = f"{scheme}://{host}"
    host = host.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        headers = {
            'Content-Type': 'application/json',
            'X-NITRO-USER': username,
            'X-NITRO-PASS': password
        }
        
        # Login and get session
        login_data = {
            'login': {
                'username': username,
                'password': password
            }
        }
        
        response = session.post(f"{host}/nitro/v1/config/login",
                               json=login_data, headers={'Content-Type': 'application/json'},
                               timeout=15)
        
        if response.status_code == 201:
            # Get system info
            headers['Cookie'] = response.headers.get('Set-Cookie', '')
            
            sys_resp = session.get(f"{host}/nitro/v1/config/nsversion",
                                  headers=headers, timeout=10)
            version = 'unknown'
            if sys_resp.status_code == 200:
                version = sys_resp.json().get('nsversion', {}).get('version', 'unknown')
            
            # Get HA status
            ha_resp = session.get(f"{host}/nitro/v1/config/hanode",
                                 headers=headers, timeout=10)
            ha_status = 'Standalone'
            if ha_resp.status_code == 200:
                ha_nodes = ha_resp.json().get('hanode', [])
                if ha_nodes:
                    ha_status = ha_nodes[0].get('state', 'unknown')
            
            # Get virtual server count
            vs_resp = session.get(f"{host}/nitro/v1/config/lbvserver",
                                 headers=headers, timeout=10)
            vs_count = 0
            if vs_resp.status_code == 200:
                vs_count = len(vs_resp.json().get('lbvserver', []))
            
            # Logout
            session.post(f"{host}/nitro/v1/config/logout",
                        json={'logout': {}}, headers=headers, timeout=5)
            
            return True, f"Successfully authenticated to Citrix ADC\nVersion: {version}\nHA State: {ha_status}\nLB Virtual Servers: {vs_count}"
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
        return False, f"Citrix ADC error: {e}"

