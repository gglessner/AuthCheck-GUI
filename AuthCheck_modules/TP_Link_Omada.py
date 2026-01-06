# TP-Link Omada Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "TP-Link Omada (Wireless)"

form_fields = [
    {"name": "host", "type": "text", "label": "Controller Host", "default": "192.168.0.1"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "site", "type": "text", "label": "Site Name", "default": "Default"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Controller: 443/8043, Cloud: omada.tplinkcloud.com. admin / (set during setup)"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to TP-Link Omada Controller.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', True)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    site = form_data.get('site', 'Default').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Controller Host is required"
    if not username:
        return False, "Username is required"
    
    scheme = "https" if use_https else "http"
    base_url = f"{scheme}://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # Get controller info first
        info_resp = session.get(f"{base_url}/api/info", timeout=10)
        controller_id = None
        if info_resp.status_code == 200:
            info = info_resp.json()
            controller_id = info.get('result', {}).get('omadacId')
        
        # Login
        login_url = f"{base_url}/api/v2/login"
        if controller_id:
            login_url = f"{base_url}/{controller_id}/api/v2/login"
        
        login_data = {
            "username": username,
            "password": password
        }
        
        response = session.post(login_url, json=login_data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('errorCode') == 0:
                token = result.get('result', {}).get('token')
                
                # Get sites
                sites_url = f"{base_url}/api/v2/sites"
                if controller_id:
                    sites_url = f"{base_url}/{controller_id}/api/v2/sites"
                
                headers = {"Csrf-Token": token} if token else {}
                sites_resp = session.get(sites_url, headers=headers, timeout=10)
                
                site_count = 0
                if sites_resp.status_code == 200:
                    sites_data = sites_resp.json()
                    site_count = len(sites_data.get('result', {}).get('data', []))
                
                return True, f"Successfully authenticated to Omada Controller at {host}\nSites: {site_count}"
            else:
                return False, f"Login failed: {result.get('msg', 'Unknown error')}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Omada error: {e}"

