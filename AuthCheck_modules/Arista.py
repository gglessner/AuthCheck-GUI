# Arista Networks Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Arista Networks (Network)"

form_fields = [
    {"name": "host", "type": "text", "label": "Switch Host"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "protocol", "type": "combo", "label": "Protocol", "options": ["https", "http"], "default": "https"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / (no password by default). eAPI must be enabled: management api http-commands."},
]


def authenticate(form_data):
    """Attempt to authenticate to Arista switch via eAPI."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    protocol = form_data.get('protocol', 'https')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Switch Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        url = f"{protocol}://{host}/command-api"
        auth = HTTPBasicAuth(username, password)
        headers = {'Content-Type': 'application/json'}
        
        # eAPI request format
        payload = {
            'jsonrpc': '2.0',
            'method': 'runCmds',
            'params': {
                'version': 1,
                'cmds': ['show version', 'show interfaces status | count'],
                'format': 'json'
            },
            'id': 1
        }
        
        response = requests.post(url, json=payload, auth=auth,
                                headers=headers, verify=verify_ssl, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'result' in data:
                results = data['result']
                
                # Parse version info
                version_info = results[0] if len(results) > 0 else {}
                model = version_info.get('modelName', 'unknown')
                version = version_info.get('version', 'unknown')
                hostname = version_info.get('hostname', 'unknown')
                uptime = version_info.get('uptime', 0)
                
                # Format uptime
                uptime_days = uptime // 86400
                uptime_hours = (uptime % 86400) // 3600
                
                return True, f"Successfully authenticated to Arista\nHostname: {hostname}\nModel: {model}\nEOS Version: {version}\nUptime: {uptime_days}d {uptime_hours}h"
            elif 'error' in data:
                error_msg = data['error'].get('message', 'Unknown error')
                return False, f"eAPI error: {error_msg}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Arista error: {e}"

