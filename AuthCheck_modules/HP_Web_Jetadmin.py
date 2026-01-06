# HP Web Jetadmin Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "HP Web Jetadmin (Printer)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8443",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8000"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / (set during install). Default ports: 8000 (HTTP), 8443 (HTTPS)"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to HP Web Jetadmin.
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
        
        # Get version info
        info_url = f"{base_url}/hpwja/"
        info_resp = session.get(info_url, timeout=10)
        
        version = "unknown"
        if info_resp.status_code == 200:
            import re
            match = re.search(r'Version\s*:?\s*([\d.]+)', info_resp.text)
            if match:
                version = match.group(1)
        
        # Web Jetadmin login
        login_url = f"{base_url}/hpwja/wja/login"
        login_data = {
            "username": username,
            "password": password
        }
        
        response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
        
        if response.status_code == 200:
            if "logout" in response.text.lower() or "dashboard" in response.text.lower():
                # Get device count
                devices_url = f"{base_url}/hpwja/wja/devices"
                devices_resp = session.get(devices_url, timeout=10)
                
                device_count = 0
                if devices_resp.status_code == 200:
                    try:
                        data = devices_resp.json()
                        device_count = len(data.get('devices', []))
                    except:
                        pass
                
                return True, f"Successfully authenticated to HP Web Jetadmin {version}\nManaged devices: {device_count}"
            elif "invalid" in response.text.lower() or "failed" in response.text.lower():
                return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"HP Web Jetadmin error: {e}"

