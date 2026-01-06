# Dell EMC PowerStore Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Dell EMC PowerStore (Storage)"

form_fields = [
    {"name": "host", "type": "text", "label": "PowerStore Host"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / (set during initial configuration). REST API on port 443."},
]


def authenticate(form_data):
    """Attempt to authenticate to Dell EMC PowerStore."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "PowerStore Host is required"
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
        
        # Get cluster info
        response = session.get(f"{host}/api/rest/cluster", headers=headers, timeout=10)
        
        if response.status_code == 200:
            clusters = response.json()
            if clusters:
                cluster = clusters[0]
                cluster_name = cluster.get('name', 'unknown')
                
                # Get appliance info
                appliance_resp = session.get(f"{host}/api/rest/appliance", headers=headers, timeout=10)
                model = 'unknown'
                serial = 'unknown'
                sw_version = 'unknown'
                if appliance_resp.status_code == 200:
                    appliances = appliance_resp.json()
                    if appliances:
                        model = appliances[0].get('model', 'unknown')
                        serial = appliances[0].get('serial_number', 'unknown')
                        sw_version = appliances[0].get('software_installed', {}).get('release_version', 'unknown')
                
                # Get volume count
                vol_resp = session.get(f"{host}/api/rest/volume", headers=headers, timeout=10)
                vol_count = len(vol_resp.json()) if vol_resp.status_code == 200 else 0
                
                return True, f"Successfully authenticated to Dell EMC PowerStore\nCluster: {cluster_name}\nModel: {model}\nVersion: {sw_version}\nVolumes: {vol_count}"
            else:
                return True, f"Successfully authenticated to Dell EMC PowerStore at {host}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Dell EMC PowerStore error: {e}"

