# Fortinet FortiAP Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Fortinet FortiAP (Wireless)"

form_fields = [
    {"name": "host", "type": "text", "label": "FortiGate Host", "default": "192.168.1.99"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "api_key", "type": "password", "label": "API Key (alternative)"},
    {"name": "vdom", "type": "text", "label": "VDOM", "default": "root"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "FortiAPs managed via FortiGate. HTTPS: 443. admin / (blank or set)"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to FortiGate to manage FortiAPs.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    api_key = form_data.get('api_key', '').strip()
    vdom = form_data.get('vdom', 'root').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "FortiGate Host is required"
    
    base_url = f"https://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        headers = {}
        
        if api_key:
            headers['Authorization'] = f"Bearer {api_key}"
        else:
            # Login with username/password
            login_url = f"{base_url}/logincheck"
            login_data = {
                "username": username,
                "secretkey": password
            }
            
            response = session.post(login_url, data=login_data, timeout=15)
            
            # Check for CSRF token
            for cookie in session.cookies:
                if 'ccsrftoken' in cookie.name.lower():
                    headers['X-CSRFTOKEN'] = cookie.value.strip('"')
        
        # Get FortiAP list
        ap_url = f"{base_url}/api/v2/monitor/wifi/managed_ap"
        params = {"vdom": vdom}
        
        response = session.get(ap_url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            aps = data.get('results', [])
            ap_count = len(aps)
            
            online_count = sum(1 for ap in aps if ap.get('status') == 'online')
            
            return True, f"Successfully authenticated to FortiGate at {host}\nManaged FortiAPs: {ap_count}\nOnline: {online_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Access forbidden: Check API permissions"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"FortiAP error: {e}"

