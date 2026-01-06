# Yealink Device Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Yealink (PBX)"

form_fields = [
    {"name": "host", "type": "text", "label": "Yealink Device IP"},
    {"name": "port", "type": "text", "label": "HTTP Port", "default": "80"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password", "default": "admin"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: admin/admin. Web interface for IP phones."},
]


def authenticate(form_data):
    """Attempt to authenticate to Yealink device."""
    try:
        import requests
        from requests.auth import HTTPDigestAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '80').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    if not host:
        return False, "Yealink Device IP is required"
    if not username:
        return False, "Username is required"
    
    try:
        base_url = f"http://{host}:{port}"
        
        # Try basic auth first
        response = requests.get(
            f"{base_url}/servlet?m=mod_data&p=status-dev&q=load",
            auth=(username, password),
            timeout=15
        )
        
        if response.status_code == 401:
            # Try digest auth
            response = requests.get(
                f"{base_url}/servlet?m=mod_data&p=status-dev&q=load",
                auth=HTTPDigestAuth(username, password),
                timeout=15
            )
        
        if response.status_code == 200:
            try:
                data = response.json()
                model = data.get('model', 'unknown')
                firmware = data.get('firmware', 'unknown')
                mac = data.get('mac', 'unknown')
                
                return True, f"Successfully authenticated to Yealink\nHost: {host}:{port}\nModel: {model}\nFirmware: {firmware}\nMAC: {mac}"
            except:
                return True, f"Successfully authenticated to Yealink\nHost: {host}:{port}\nWeb interface accessible"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Yealink error: {e}"

