# Fortinet FortiGate Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Fortinet FortiGate (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "FortiGate Host"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "api_key", "type": "password", "label": "API Key (Alternative)"},
    {"name": "vdom", "type": "text", "label": "VDOM", "default": "root"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / (no password by default). API key from System > Administrators."},
]


def authenticate(form_data):
    """Attempt to authenticate to Fortinet FortiGate."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    username = form_data.get('username', 'admin').strip()
    password = form_data.get('password', '')
    api_key = form_data.get('api_key', '').strip()
    vdom = form_data.get('vdom', 'root').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "FortiGate Host is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        if api_key:
            # API key authentication
            headers = {'Authorization': f'Bearer {api_key}'}
            response = session.get(f"{host}/api/v2/cmdb/system/global?vdom={vdom}",
                                  headers=headers, timeout=15)
        else:
            # Session-based authentication
            if not username:
                return False, "Username or API Key is required"
            
            # Login
            login_data = {
                'username': username,
                'secretkey': password
            }
            login_resp = session.post(f"{host}/logincheck",
                                     data=login_data, timeout=15)
            
            if 'error' in login_resp.text.lower():
                return False, "Authentication failed: Invalid credentials"
            
            headers = {}
            response = session.get(f"{host}/api/v2/cmdb/system/global?vdom={vdom}",
                                  headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Get system status
            status_resp = session.get(f"{host}/api/v2/monitor/system/status?vdom={vdom}",
                                     headers=headers if api_key else {}, timeout=10)
            
            version = 'unknown'
            hostname = 'unknown'
            serial = 'unknown'
            
            if status_resp.status_code == 200:
                status_data = status_resp.json().get('results', {})
                version = status_data.get('version', 'unknown')
                hostname = status_data.get('hostname', 'unknown')
                serial = status_data.get('serial', 'unknown')
            
            # Get policy count
            policy_resp = session.get(f"{host}/api/v2/cmdb/firewall/policy?vdom={vdom}",
                                     headers=headers if api_key else {}, timeout=10)
            policy_count = 0
            if policy_resp.status_code == 200:
                policy_count = len(policy_resp.json().get('results', []))
            
            return True, f"Successfully authenticated to FortiGate\nHostname: {hostname}\nVersion: {version}\nSerial: {serial}\nPolicies: {policy_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Authentication failed: Insufficient permissions"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"FortiGate error: {e}"

