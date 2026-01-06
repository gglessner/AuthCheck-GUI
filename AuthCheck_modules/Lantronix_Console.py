# Lantronix Console Server Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Lantronix Console/SLC (Console)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.100"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "sysadmin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "sysadmin / PASS (default). HTTPS: 443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Lantronix SLC/Console Manager.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
    use_https = form_data.get('use_https', True)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    scheme = "https" if use_https else "http"
    base_url = f"{scheme}://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # Lantronix web login
        login_url = f"{base_url}/cgi-bin/login"
        login_data = {
            "username": username,
            "password": password
        }
        
        response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
        
        if response.status_code == 200:
            if "logout" in response.text.lower() or "dashboard" in response.text.lower():
                import re
                
                model = "Lantronix"
                ver_match = re.search(r'firmware["\s:]+([0-9.]+)', response.text, re.IGNORECASE)
                firmware = ver_match.group(1) if ver_match else "unknown"
                
                return True, f"Successfully authenticated to {model} at {host}\nFirmware: {firmware}"
            elif "invalid" in response.text.lower():
                return False, "Authentication failed: Invalid credentials"
        
        # Try basic auth
        response = session.get(f"{base_url}/status", auth=(username, password), timeout=15)
        
        if response.status_code == 200:
            return True, f"Successfully authenticated to Lantronix at {host}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Lantronix error: {e}"

