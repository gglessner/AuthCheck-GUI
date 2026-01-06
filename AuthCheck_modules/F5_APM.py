# F5 BIG-IP APM Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "F5 BIG-IP APM (VPN)"

form_fields = [
    {"name": "host", "type": "text", "label": "APM Host", "default": "vpn.example.com"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "BIG-IP Access Policy Manager. HTTPS: 443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to F5 BIG-IP APM.
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
        
        # Get the logon page to get session cookie
        logon_url = f"{base_url}/my.policy"
        session.get(logon_url, timeout=15)
        
        # APM login
        login_url = f"{base_url}/my.policy"
        login_data = {
            "username": username,
            "password": password
        }
        
        response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
        
        if response.status_code == 200:
            if "MRHSession" in session.cookies or "webtop" in response.url:
                return True, f"Successfully authenticated to F5 APM at {host}"
            elif "Invalid" in response.text or "logon failed" in response.text.lower():
                return False, "Authentication failed: Invalid credentials"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"F5 APM error: {e}"

