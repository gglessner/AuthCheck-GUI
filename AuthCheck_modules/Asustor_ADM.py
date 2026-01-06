# Asustor ADM Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Asustor ADM (NAS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.100"},
    {"name": "port", "type": "text", "label": "Port", "default": "8001",
     "port_toggle": "use_https", "tls_port": "8001", "non_tls_port": "8000"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / admin (default). HTTP: 8000, HTTPS: 8001"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Asustor ADM.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8001').strip()
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
        
        # ADM login API
        login_url = f"{base_url}/portal/apis/login.cgi"
        login_data = {
            "account": username,
            "password": password
        }
        
        response = session.post(login_url, data=login_data, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success") or data.get("sid"):
                # Get system info
                info_url = f"{base_url}/portal/apis/sysinfo.cgi"
                info_resp = session.get(info_url, timeout=10)
                
                model = "Asustor NAS"
                adm_version = "unknown"
                if info_resp.status_code == 200:
                    info_data = info_resp.json()
                    model = info_data.get("model", "Asustor NAS")
                    adm_version = info_data.get("version", "unknown")
                
                return True, f"Successfully authenticated to {model}\nADM Version: {adm_version}"
            else:
                return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Asustor error: {e}"

