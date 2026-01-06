# HID VertX/Edge Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "HID VertX/Edge (Access Control)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.100"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "root / vertx or edge (default). HTTPS: 443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to HID VertX/Edge access control.
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
        
        # VertX/Edge web login
        login_url = f"{base_url}/cgi-bin/vertx_cgi.cgi"
        login_data = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?><VertXMessage><hid:Login><userName>{username}</userName><password>{password}</password></hid:Login></VertXMessage>"
        
        headers = {"Content-Type": "application/xml"}
        
        response = session.post(login_url, data=login_data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            if "validCredentials=\"true\"" in response.text or "<validCredentials>true</validCredentials>" in response.text:
                import re
                
                version = "unknown"
                ver_match = re.search(r'firmware["\s:]+([0-9.]+)', response.text, re.IGNORECASE)
                if ver_match:
                    version = ver_match.group(1)
                
                return True, f"Successfully authenticated to HID VertX/Edge at {host}\nFirmware: {version}"
            elif "validCredentials=\"false\"" in response.text:
                return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        # Try basic auth
        response = session.get(f"{base_url}/status.xml", auth=(username, password), timeout=15)
        
        if response.status_code == 200:
            return True, f"Successfully authenticated to HID VertX/Edge at {host}"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"HID VertX/Edge error: {e}"
