# Lenovo XCC/IMM Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Lenovo XCC/IMM (BMC)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.0.120"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "bmc_type", "type": "combo", "label": "BMC Type",
     "options": ["XCC (ThinkSystem)", "IMM2 (System x)", "IMM (older)"]},
    {"name": "username", "type": "text", "label": "Username", "default": "USERID"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "USERID / PASSW0RD (default). HTTPS: 443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Lenovo XCC or IMM.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
    bmc_type = form_data.get('bmc_type', 'XCC (ThinkSystem)')
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
        
        # Try Redfish API (XCC and newer IMM2)
        redfish_url = f"{base_url}/redfish/v1"
        response = session.get(redfish_url, auth=(username, password), timeout=15)
        
        if response.status_code == 200:
            # Get system info
            systems_url = f"{base_url}/redfish/v1/Systems/1"
            sys_resp = session.get(systems_url, auth=(username, password), timeout=10)
            
            model = "Lenovo Server"
            if sys_resp.status_code == 200:
                sys_data = sys_resp.json()
                model = sys_data.get('Model', 'Lenovo Server')
            
            # Get BMC info
            mgr_url = f"{base_url}/redfish/v1/Managers/1"
            mgr_resp = session.get(mgr_url, auth=(username, password), timeout=10)
            
            bmc_model = "XCC"
            firmware = "unknown"
            if mgr_resp.status_code == 200:
                mgr_data = mgr_resp.json()
                bmc_model = mgr_data.get('Model', 'XCC')
                firmware = mgr_data.get('FirmwareVersion', 'unknown')
            
            return True, f"Successfully authenticated to {bmc_model} at {host}\nServer: {model}\nFirmware: {firmware}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        # Try IMM web login
        login_url = f"{base_url}/data/login"
        login_data = {
            "user": username,
            "password": password
        }
        
        response = session.post(login_url, data=login_data, timeout=15)
        
        if response.status_code == 200:
            if "authResult" in response.text and "ok" in response.text.lower():
                return True, f"Successfully authenticated to IMM at {host}"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Lenovo BMC error: {e}"

