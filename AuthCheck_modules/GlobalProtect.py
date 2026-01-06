# Palo Alto GlobalProtect VPN Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Palo Alto GlobalProtect (VPN)"

form_fields = [
    {"name": "host", "type": "text", "label": "Portal Host", "default": "vpn.example.com"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "GlobalProtect portal. HTTPS: 443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Palo Alto GlobalProtect.
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
        
        # GlobalProtect prelogin
        prelogin_url = f"{base_url}/global-protect/prelogin.esp"
        prelogin_resp = session.get(prelogin_url, timeout=15)
        
        # GlobalProtect login
        login_url = f"{base_url}/global-protect/getconfig.esp"
        login_data = {
            "user": username,
            "passwd": password,
            "clientos": "Windows",
            "clientver": "5.0.0"
        }
        
        response = session.post(login_url, data=login_data, timeout=15)
        
        if response.status_code == 200:
            if "<status>success</status>" in response.text.lower():
                import re
                
                gateways = []
                gateway_matches = re.findall(r'<gateways>.*?</gateways>', response.text, re.DOTALL)
                
                return True, f"Successfully authenticated to GlobalProtect at {host}"
            elif "<status>error</status>" in response.text.lower():
                if "Invalid username or password" in response.text:
                    return False, "Authentication failed: Invalid credentials"
                else:
                    import re
                    error_match = re.search(r'<error>(.*?)</error>', response.text)
                    error_msg = error_match.group(1) if error_match else "Unknown error"
                    return False, f"Authentication failed: {error_msg}"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"GlobalProtect error: {e}"

