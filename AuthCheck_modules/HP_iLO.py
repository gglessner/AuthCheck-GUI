# HP iLO Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "HP iLO (BMC)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.0.120"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": "Administrator"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Administrator / (on tag). HTTPS: 443, SSH: 22"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to HP Integrated Lights-Out (iLO).
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
        
        # Try Redfish API (iLO 4+)
        redfish_url = f"{base_url}/redfish/v1"
        response = session.get(redfish_url, auth=(username, password), timeout=15)
        
        if response.status_code == 200:
            # Get system info
            systems_url = f"{base_url}/redfish/v1/Systems/1"
            sys_resp = session.get(systems_url, auth=(username, password), timeout=10)
            
            model = "HP Server"
            if sys_resp.status_code == 200:
                sys_data = sys_resp.json()
                model = sys_data.get('Model', 'HP Server')
            
            # Get iLO info
            mgr_url = f"{base_url}/redfish/v1/Managers/1"
            mgr_resp = session.get(mgr_url, auth=(username, password), timeout=10)
            
            ilo_version = "unknown"
            firmware = "unknown"
            if mgr_resp.status_code == 200:
                mgr_data = mgr_resp.json()
                ilo_version = mgr_data.get('Model', 'iLO')
                firmware = mgr_data.get('FirmwareVersion', 'unknown')
            
            return True, f"Successfully authenticated to {ilo_version} at {host}\nServer: {model}\nFirmware: {firmware}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        # Try legacy RIBCL (iLO 2/3)
        ribcl_url = f"{base_url}/ribcl"
        ribcl_data = f'''<?xml version="1.0"?>
        <RIBCL VERSION="2.0">
            <LOGIN USER_LOGIN="{username}" PASSWORD="{password}">
                <SERVER_INFO MODE="read">
                    <GET_HOST_DATA/>
                </SERVER_INFO>
            </LOGIN>
        </RIBCL>'''
        
        headers = {"Content-Type": "application/xml"}
        response = session.post(ribcl_url, data=ribcl_data, headers=headers, timeout=15)
        
        if response.status_code == 200 and "HOST_DATA" in response.text:
            return True, f"Successfully authenticated to iLO at {host}"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"iLO error: {e}"

