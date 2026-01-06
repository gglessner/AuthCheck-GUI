# Xerox Printer Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Xerox Printer (Printer)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.100"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / 1111. CentreWare: 80/443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Xerox Printer/MFP.
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
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    scheme = "https" if use_https else "http"
    base_url = f"{scheme}://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # Get device info
        info_url = f"{base_url}/ssm/Management/Anonymous/StatusConfig"
        info_resp = session.get(info_url, timeout=10)
        
        model = "Xerox Printer"
        if info_resp.status_code == 200:
            import re
            match = re.search(r'"modelName"\s*:\s*"([^"]+)"', info_resp.text)
            if match:
                model = match.group(1)
        
        # Login
        login_url = f"{base_url}/ssm/Account/Logout"
        session.get(login_url, timeout=5)  # Clear any existing session
        
        login_url = f"{base_url}/ssm/Account/Login"
        login_data = {
            "username": username,
            "password": password
        }
        
        response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
        
        if response.status_code == 200:
            if "logout" in response.text.lower() or "authenticated" in response.text.lower():
                return True, f"Successfully authenticated to {model} at {host}"
            elif "invalid" in response.text.lower() or "failed" in response.text.lower():
                return False, "Authentication failed: Invalid credentials"
        
        # Try alternative login method (older Xerox)
        login_url = f"{base_url}/set_auth.html"
        login_data = {
            "AuthMethodValue": "LOCAL",
            "LoginName": username,
            "Password": password
        }
        
        response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
        
        if response.status_code == 200 and "success" in response.text.lower():
            return True, f"Successfully authenticated to {model} at {host}"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Xerox error: {e}"

