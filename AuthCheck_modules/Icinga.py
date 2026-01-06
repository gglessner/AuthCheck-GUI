# Icinga Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Icinga (Monitoring)"

form_fields = [
    {"name": "host", "type": "text", "label": "Icinga Host"},
    {"name": "port", "type": "text", "label": "API Port", "default": "5665"},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: root/icinga. API port 5665. Requires API feature enabled."},
]


def authenticate(form_data):
    """Attempt to authenticate to Icinga."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '5665').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Icinga Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        url = f"https://{host}:{port}"
        
        # Get status
        response = requests.get(
            f"{url}/v1/status",
            auth=(username, password),
            verify=verify_ssl,
            headers={'Accept': 'application/json'},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json().get('results', [])
            
            # Parse status data
            icinga_status = {}
            for item in data:
                name = item.get('name', '')
                if name == 'IcingaApplication':
                    icinga_status = item.get('status', {}).get('icingaapplication', {}).get('app', {})
            
            version = icinga_status.get('version', 'unknown')
            node_name = icinga_status.get('node_name', 'unknown')
            
            # Get hosts count
            hosts_resp = requests.get(
                f"{url}/v1/objects/hosts",
                auth=(username, password),
                verify=verify_ssl,
                headers={'Accept': 'application/json'},
                timeout=10
            )
            host_count = 0
            if hosts_resp.status_code == 200:
                host_count = len(hosts_resp.json().get('results', []))
            
            # Get services count
            svc_resp = requests.get(
                f"{url}/v1/objects/services",
                auth=(username, password),
                verify=verify_ssl,
                headers={'Accept': 'application/json'},
                timeout=10
            )
            svc_count = 0
            if svc_resp.status_code == 200:
                svc_count = len(svc_resp.json().get('results', []))
            
            return True, f"Successfully authenticated to Icinga\nNode: {node_name}\nVersion: {version}\nHosts: {host_count}\nServices: {svc_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Icinga error: {e}"

