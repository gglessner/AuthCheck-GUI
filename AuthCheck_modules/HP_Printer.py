# HP Printer Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "HP Printer (Printer)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.100"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "EWS: 80/443. admin / (blank or set). JetDirect: 9100"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to HP Printer Embedded Web Server (EWS).
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
        
        # Try to get device info first (no auth needed for some pages)
        info_url = f"{base_url}/DevMgmt/ProductConfigDyn.xml"
        info_resp = session.get(info_url, timeout=10)
        
        model = "HP Printer"
        if info_resp.status_code == 200:
            import re
            match = re.search(r'<prdcfgdyn:ProductName[^>]*>([^<]+)</prdcfgdyn:ProductName>', info_resp.text)
            if match:
                model = match.group(1)
        
        # Try authentication
        if username or password:
            # HP EWS uses digest auth or form-based
            from requests.auth import HTTPDigestAuth, HTTPBasicAuth
            
            # Try digest auth first (more common for HP)
            auth_url = f"{base_url}/hp/device/this.LCDispatcher"
            response = session.get(auth_url, auth=HTTPDigestAuth(username, password), timeout=15)
            
            if response.status_code == 200:
                return True, f"Successfully authenticated to {model} at {host}"
            elif response.status_code == 401:
                # Try basic auth
                response = session.get(auth_url, auth=HTTPBasicAuth(username, password), timeout=15)
                if response.status_code == 200:
                    return True, f"Successfully authenticated to {model} at {host}"
                return False, "Authentication failed: Invalid credentials"
        else:
            # Check if printer is accessible without auth
            response = session.get(base_url, timeout=10)
            if response.status_code == 200:
                if "hp" in response.text.lower() or "laserjet" in response.text.lower():
                    return True, f"Connected to {model} at {host} (no authentication required)"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"HP Printer error: {e}"

