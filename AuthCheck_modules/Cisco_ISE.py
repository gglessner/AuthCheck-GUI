# Cisco ISE Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Cisco ISE (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "ISE Host"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / (set during setup). ERS API on port 9060. Enable ERS in Admin > System > Settings."},
]


def authenticate(form_data):
    """Attempt to authenticate to Cisco ISE."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "ISE Host is required"
    if not username:
        return False, "Username is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        session.auth = (username, password)
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Try ERS API
        response = session.get(f"{host}:9060/ers/config/adminuser",
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            admin_count = data.get('SearchResult', {}).get('total', 0)
            
            # Get network device count
            devices_resp = session.get(f"{host}:9060/ers/config/networkdevice",
                                       headers=headers, timeout=10)
            device_count = 0
            if devices_resp.status_code == 200:
                device_count = devices_resp.json().get('SearchResult', {}).get('total', 0)
            
            # Get endpoint count
            endpoints_resp = session.get(f"{host}:9060/ers/config/endpoint",
                                        headers=headers, timeout=10)
            endpoint_count = 0
            if endpoints_resp.status_code == 200:
                endpoint_count = endpoints_resp.json().get('SearchResult', {}).get('total', 0)
            
            return True, f"Successfully authenticated to Cisco ISE\nUser: {username}\nAdmin Users: {admin_count}\nNetwork Devices: {device_count}\nEndpoints: {endpoint_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Authentication failed: ERS API may be disabled or user lacks permissions"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Cisco ISE error: {e}"

