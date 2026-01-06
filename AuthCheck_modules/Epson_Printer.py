# Epson Printer Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Epson Printer (Printer)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.100"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username", "default": "epson"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "epson / (serial number last 4 digits) or admin / admin. EpsonNet: 80/443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Epson Printer Web Config.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
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
        info_url = f"{base_url}/PRESENTATION/HTML/TOP/INDEX.HTML"
        info_resp = session.get(info_url, timeout=10)
        
        model = "Epson Printer"
        if info_resp.status_code == 200:
            import re
            match = re.search(r'<title>([^<]+)</title>', info_resp.text, re.IGNORECASE)
            if match:
                model = match.group(1).strip()
        
        # Epson uses digest or basic auth
        from requests.auth import HTTPDigestAuth, HTTPBasicAuth
        
        # Try digest auth first
        config_url = f"{base_url}/PRESENTATION/HTML/TOP/PRTINFO.HTML"
        response = session.get(config_url, auth=HTTPDigestAuth(username, password), timeout=15)
        
        if response.status_code == 200:
            return True, f"Successfully authenticated to {model} at {host}"
        elif response.status_code == 401:
            # Try basic auth
            response = session.get(config_url, auth=HTTPBasicAuth(username, password), timeout=15)
            if response.status_code == 200:
                return True, f"Successfully authenticated to {model} at {host}"
            return False, "Authentication failed: Invalid credentials"
        
        # Try form-based login (newer models)
        login_url = f"{base_url}/Login.html"
        login_data = {
            "userid": username,
            "password": password
        }
        
        response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
        
        if response.status_code == 200 and "logout" in response.text.lower():
            return True, f"Successfully authenticated to {model} at {host}"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Epson error: {e}"

