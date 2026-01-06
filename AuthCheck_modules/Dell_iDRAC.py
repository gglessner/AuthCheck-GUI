# Dell iDRAC Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Dell iDRAC (BMC)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.0.120"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "root / calvin (default). HTTPS: 443, SSH: 22, Redfish API"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Dell iDRAC.
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
        
        # Try Redfish API first (iDRAC 7+)
        redfish_url = f"{base_url}/redfish/v1"
        response = session.get(redfish_url, auth=(username, password), timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Get system info
            systems_url = f"{base_url}/redfish/v1/Systems/System.Embedded.1"
            sys_resp = session.get(systems_url, auth=(username, password), timeout=10)
            
            model = "Dell Server"
            if sys_resp.status_code == 200:
                sys_data = sys_resp.json()
                model = sys_data.get('Model', 'Dell Server')
            
            # Get iDRAC info
            mgr_url = f"{base_url}/redfish/v1/Managers/iDRAC.Embedded.1"
            mgr_resp = session.get(mgr_url, auth=(username, password), timeout=10)
            
            idrac_version = "unknown"
            if mgr_resp.status_code == 200:
                mgr_data = mgr_resp.json()
                idrac_version = mgr_data.get('FirmwareVersion', 'unknown')
            
            return True, f"Successfully authenticated to iDRAC at {host}\nServer: {model}\niDRAC Version: {idrac_version}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        # Try legacy web login (iDRAC 6 and older)
        login_url = f"{base_url}/data/login"
        login_data = {
            "user": username,
            "password": password
        }
        
        response = session.post(login_url, data=login_data, timeout=15)
        
        if response.status_code == 200 and "authResult" in response.text:
            if "0" in response.text:  # Success
                return True, f"Successfully authenticated to iDRAC at {host}"
            else:
                return False, "Authentication failed: Invalid credentials"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"iDRAC error: {e}"

