# Ubiquiti UniFi Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Ubiquiti UniFi (Network)"

form_fields = [
    {"name": "host", "type": "text", "label": "Controller Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "8443"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "site", "type": "text", "label": "Site ID", "default": "default"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "(set at install). Default port 8443. Site ID 'default' for default site."},
]


def authenticate(form_data):
    """Attempt to authenticate to Ubiquiti UniFi Controller."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8443').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    site = form_data.get('site', 'default').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Controller Host is required"
    if not username:
        return False, "Username is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # Login
        login_resp = session.post(
            f"{host}:{port}/api/login",
            json={'username': username, 'password': password},
            timeout=15
        )
        
        if login_resp.status_code == 200:
            # Get controller info
            sysinfo_resp = session.get(f"{host}:{port}/api/s/{site}/stat/sysinfo",
                                      timeout=10)
            version = 'unknown'
            if sysinfo_resp.status_code == 200:
                sysinfo = sysinfo_resp.json().get('data', [{}])[0]
                version = sysinfo.get('version', 'unknown')
            
            # Get device count
            devices_resp = session.get(f"{host}:{port}/api/s/{site}/stat/device",
                                      timeout=10)
            device_count = 0
            if devices_resp.status_code == 200:
                device_count = len(devices_resp.json().get('data', []))
            
            # Get client count
            clients_resp = session.get(f"{host}:{port}/api/s/{site}/stat/sta",
                                      timeout=10)
            client_count = 0
            if clients_resp.status_code == 200:
                client_count = len(clients_resp.json().get('data', []))
            
            # Logout
            session.post(f"{host}:{port}/api/logout", timeout=5)
            
            return True, f"Successfully authenticated to UniFi Controller {version}\nSite: {site}\nDevices: {device_count}\nClients: {client_count}"
        elif login_resp.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {login_resp.status_code}: {login_resp.text[:200]}"
            
    except Exception as e:
        return False, f"UniFi error: {e}"

