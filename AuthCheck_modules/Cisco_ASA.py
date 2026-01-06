# Cisco ASA Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Cisco ASA/ASDM (VPN)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.1"},
    {"name": "port", "type": "text", "label": "HTTPS Port", "default": "443"},
    {"name": "auth_method", "type": "combo", "label": "Auth Method",
     "options": ["ASDM", "REST API"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "cisco / cisco, enable password. ASDM: 443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Cisco ASA via ASDM or REST API.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
    auth_method = form_data.get('auth_method', 'ASDM')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    base_url = f"https://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        if auth_method == "REST API":
            # REST API authentication
            token_url = f"{base_url}/api/tokenservices"
            headers = {"Content-Type": "application/json"}
            
            response = session.post(token_url, auth=(username, password), headers=headers, timeout=15)
            
            if response.status_code == 204:
                token = response.headers.get('X-Auth-Token')
                
                # Get version
                version_url = f"{base_url}/api/monitoring/serialnumber"
                headers['X-Auth-Token'] = token
                ver_resp = session.get(version_url, headers=headers, timeout=10)
                
                serial = "unknown"
                if ver_resp.status_code == 200:
                    serial = ver_resp.json().get('serialNumber', 'unknown')
                
                # Logout
                session.delete(token_url, headers=headers, timeout=5)
                
                return True, f"Successfully authenticated to Cisco ASA at {host}\nSerial: {serial}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
        else:
            # ASDM authentication
            asdm_url = f"{base_url}/admin/exec/show%20version"
            
            response = session.get(asdm_url, auth=(username, password), timeout=15)
            
            if response.status_code == 200:
                import re
                version = "unknown"
                ver_match = re.search(r'Cisco Adaptive Security Appliance Software Version ([0-9.()]+)', response.text)
                if ver_match:
                    version = ver_match.group(1)
                
                return True, f"Successfully authenticated to Cisco ASA at {host}\nVersion: {version}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Cisco ASA error: {e}"

