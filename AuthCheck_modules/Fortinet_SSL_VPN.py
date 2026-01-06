# Fortinet SSL VPN Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Fortinet SSL VPN (VPN)"

form_fields = [
    {"name": "host", "type": "text", "label": "VPN Host", "default": "vpn.example.com"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "realm", "type": "text", "label": "Realm"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "FortiGate SSL VPN. HTTPS: 443/10443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Fortinet SSL VPN.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
    realm = form_data.get('realm', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    base_url = f"https://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # FortiGate SSL VPN login
        login_url = f"{base_url}/remote/logincheck"
        login_data = {
            "ajax": "1",
            "username": username,
            "credential": password,
            "realm": realm
        }
        
        response = session.post(login_url, data=login_data, timeout=15)
        
        if response.status_code == 200:
            if "redir" in response.text or "ret=1" in response.text:
                return True, f"Successfully authenticated to Fortinet SSL VPN at {host}"
            elif "ret=0" in response.text or "failed" in response.text.lower():
                return False, "Authentication failed: Invalid credentials"
        
        # Try web portal login
        login_url = f"{base_url}/remote/login"
        login_data = {
            "username": username,
            "credential": password
        }
        
        response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
        
        if response.status_code == 200 and "portal" in response.url:
            return True, f"Successfully authenticated to Fortinet SSL VPN at {host}"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Fortinet SSL VPN error: {e}"

