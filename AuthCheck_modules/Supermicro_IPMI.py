# Supermicro IPMI Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Supermicro IPMI (BMC)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.0.120"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "ADMIN"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "ADMIN / ADMIN (default). IPMI: 623/UDP"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Supermicro IPMI/BMC.
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
        
        # Try Redfish API (newer X11/X12)
        redfish_url = f"{base_url}/redfish/v1"
        response = session.get(redfish_url, auth=(username, password), timeout=15)
        
        if response.status_code == 200:
            # Get system info
            systems_url = f"{base_url}/redfish/v1/Systems/1"
            sys_resp = session.get(systems_url, auth=(username, password), timeout=10)
            
            model = "Supermicro Server"
            if sys_resp.status_code == 200:
                sys_data = sys_resp.json()
                model = sys_data.get('Model', 'Supermicro Server')
            
            return True, f"Successfully authenticated to Supermicro BMC at {host}\nServer: {model}"
        
        # Try legacy IPMI web login
        login_url = f"{base_url}/cgi/login.cgi"
        login_data = {
            "name": username,
            "pwd": password
        }
        
        response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
        
        if response.status_code == 200:
            if "SID" in response.cookies or "logout" in response.text.lower():
                return True, f"Successfully authenticated to Supermicro IPMI at {host}"
            elif "failed" in response.text.lower() or "invalid" in response.text.lower():
                return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Supermicro IPMI error: {e}"

