# SonicWall Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "SonicWall (VPN)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.168.168"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / password (default). HTTPS: 443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to SonicWall.
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
        
        # SonicOS API auth
        auth_url = f"{base_url}/api/sonicos/auth"
        headers = {"Content-Type": "application/json"}
        
        import base64
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers["Authorization"] = f"Basic {credentials}"
        
        response = session.post(auth_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status", {}).get("success"):
                # Get version
                ver_url = f"{base_url}/api/sonicos/version"
                ver_resp = session.get(ver_url, headers=headers, timeout=10)
                
                version = "unknown"
                model = "SonicWall"
                if ver_resp.status_code == 200:
                    ver_data = ver_resp.json()
                    version = ver_data.get("firmware_version", "unknown")
                    model = ver_data.get("model", "SonicWall")
                
                return True, f"Successfully authenticated to {model} at {host}\nFirmware: {version}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        # Try legacy web login
        login_url = f"{base_url}/auth.html"
        login_data = {
            "userName": username,
            "pwd": password,
            "submit": "Login"
        }
        
        response = session.post(login_url, data=login_data, timeout=15)
        
        if response.status_code == 200 and ("main.html" in response.text or "dashboard" in response.text.lower()):
            return True, f"Successfully authenticated to SonicWall at {host}"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"SonicWall error: {e}"

