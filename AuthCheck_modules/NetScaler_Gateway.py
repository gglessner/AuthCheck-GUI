# Citrix NetScaler Gateway Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Citrix NetScaler Gateway (VPN)"

form_fields = [
    {"name": "host", "type": "text", "label": "Gateway Host", "default": "gateway.example.com"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "NetScaler Gateway/ADC. HTTPS: 443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Citrix NetScaler Gateway.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
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
        
        # NetScaler Gateway login
        login_url = f"{base_url}/cgi/login"
        login_data = {
            "login": username,
            "passwd": password
        }
        
        response = session.post(login_url, data=login_data, timeout=15)
        
        if response.status_code == 200:
            if "NSC_AAAC" in session.cookies or "portal" in response.text.lower():
                return True, f"Successfully authenticated to NetScaler Gateway at {host}"
            elif "Invalid" in response.text or "failed" in response.text.lower():
                return False, "Authentication failed: Invalid credentials"
        
        # Try vpn login endpoint
        login_url = f"{base_url}/vpn/index.html"
        login_data = {
            "login": username,
            "passwd": password,
            "Login": "Log On"
        }
        
        response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
        
        if response.status_code == 200 and "NSC_AAAC" in session.cookies:
            return True, f"Successfully authenticated to NetScaler Gateway at {host}"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"NetScaler Gateway error: {e}"

