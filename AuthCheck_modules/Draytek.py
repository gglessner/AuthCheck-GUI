# Draytek Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Draytek (Wireless)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.1"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / admin or admin / (blank). HTTP: 80, HTTPS: 443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Draytek router/AP.
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
    if not username:
        return False, "Username is required"
    
    scheme = "https" if use_https else "http"
    base_url = f"{scheme}://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # Draytek uses HTTP Basic Auth or form-based login
        # Try basic auth first
        from requests.auth import HTTPBasicAuth
        
        response = session.get(base_url, auth=HTTPBasicAuth(username, password), timeout=15)
        
        if response.status_code == 200:
            if "draytek" in response.text.lower() or "vigor" in response.text.lower():
                # Try to extract model/firmware
                import re
                model = "unknown"
                firmware = "unknown"
                
                model_match = re.search(r'Vigor\s*(\w+)', response.text, re.IGNORECASE)
                if model_match:
                    model = f"Vigor {model_match.group(1)}"
                
                fw_match = re.search(r'Firmware\s*[:=]\s*([\d.]+)', response.text)
                if fw_match:
                    firmware = fw_match.group(1)
                
                return True, f"Successfully authenticated to Draytek at {host}\nModel: {model}\nFirmware: {firmware}"
            else:
                return True, f"Successfully authenticated to device at {host}"
        elif response.status_code == 401:
            # Try form-based login
            login_url = f"{base_url}/cgi-bin/wlogin.cgi"
            login_data = {
                "aa": username,
                "ab": password
            }
            
            response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
            
            if response.status_code == 200 and "logout" in response.text.lower():
                return True, f"Successfully authenticated to Draytek at {host}"
            
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Draytek error: {e}"

