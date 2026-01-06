# VMware vCenter Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "VMware vCenter (Virtualization)"

form_fields = [
    {"name": "host", "type": "text", "label": "vCenter Host"},
    {"name": "username", "type": "text", "label": "Username", "default": "administrator@vsphere.local"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "administrator@vsphere.local / (set during install). Port 443 for vSphere API."},
]


def authenticate(form_data):
    """Attempt to authenticate to VMware vCenter."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "vCenter Host is required"
    if not username:
        return False, "Username is required"
    
    # Normalize host
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        # Try REST API authentication (vSphere 6.5+)
        session = requests.Session()
        session.verify = verify_ssl
        
        auth_url = f"{host}/api/session"
        response = session.post(auth_url, auth=(username, password), timeout=10)
        
        if response.status_code == 201:
            session_token = response.json()
            
            # Get vCenter info
            headers = {'vmware-api-session-id': session_token}
            
            # Get system info
            about_resp = session.get(f"{host}/api/vcenter/system/config/global/info",
                                    headers=headers, timeout=10)
            
            # Get host count
            hosts_resp = session.get(f"{host}/api/vcenter/host",
                                    headers=headers, timeout=10)
            host_count = 0
            if hosts_resp.status_code == 200:
                host_count = len(hosts_resp.json())
            
            # Get VM count
            vms_resp = session.get(f"{host}/api/vcenter/vm",
                                  headers=headers, timeout=10)
            vm_count = 0
            if vms_resp.status_code == 200:
                vm_count = len(vms_resp.json())
            
            # Get datacenter count
            dc_resp = session.get(f"{host}/api/vcenter/datacenter",
                                 headers=headers, timeout=10)
            dc_count = 0
            if dc_resp.status_code == 200:
                dc_count = len(dc_resp.json())
            
            # Logout
            session.delete(auth_url, headers=headers, timeout=5)
            
            return True, f"Successfully authenticated to vCenter\nUser: {username}\nDatacenters: {dc_count}\nHosts: {host_count}\nVMs: {vm_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"vCenter error: {e}"

