# Pulse Secure/Ivanti VPN Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Pulse Secure/Ivanti (VPN)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "vpn.example.com"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "realm", "type": "text", "label": "Realm", "default": "Users"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Admin realm: Administrators. HTTPS: 443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Pulse Secure/Ivanti Connect Secure.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
    realm = form_data.get('realm', 'Users').strip()
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
        
        # Pulse Secure login
        login_url = f"{base_url}/dana-na/auth/url_default/login.cgi"
        login_data = {
            "tz_offset": "0",
            "username": username,
            "password": password,
            "realm": realm,
            "btnSubmit": "Sign In"
        }
        
        response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
        
        if response.status_code == 200:
            if "welcome.cgi" in response.url or "DSID" in session.cookies:
                import re
                
                version = "unknown"
                ver_match = re.search(r'version["\s:]+([0-9.]+)', response.text, re.IGNORECASE)
                if ver_match:
                    version = ver_match.group(1)
                
                return True, f"Successfully authenticated to Pulse Secure at {host}\nRealm: {realm}"
            elif "Invalid username or password" in response.text:
                return False, "Authentication failed: Invalid credentials"
            elif "realm" in response.text.lower() and "invalid" in response.text.lower():
                return False, "Authentication failed: Invalid realm"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Pulse Secure error: {e}"

