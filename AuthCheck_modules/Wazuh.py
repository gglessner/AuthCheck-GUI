# Wazuh Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Wazuh (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "Wazuh Manager Host"},
    {"name": "port", "type": "text", "label": "API Port", "default": "55000"},
    {"name": "username", "type": "text", "label": "Username", "default": "wazuh"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "wazuh / wazuh (default). wazuh-wui for dashboard. API on port 55000."},
]


def authenticate(form_data):
    """Attempt to authenticate to Wazuh."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '55000').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Wazuh Manager Host is required"
    if not username:
        return False, "Username is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        # Get JWT token
        auth_resp = requests.post(
            f"{host}:{port}/security/user/authenticate",
            auth=(username, password),
            verify=verify_ssl,
            timeout=15
        )
        
        if auth_resp.status_code == 200:
            token = auth_resp.json().get('data', {}).get('token')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Get manager info
            info_resp = requests.get(f"{host}:{port}/manager/info",
                                    headers=headers, verify=verify_ssl, timeout=10)
            version = 'unknown'
            if info_resp.status_code == 200:
                info = info_resp.json().get('data', {}).get('affected_items', [{}])[0]
                version = info.get('version', 'unknown')
            
            # Get agent count
            agents_resp = requests.get(f"{host}:{port}/agents/summary/status",
                                      headers=headers, verify=verify_ssl, timeout=10)
            agent_count = 0
            active_count = 0
            if agents_resp.status_code == 200:
                summary = agents_resp.json().get('data', {})
                agent_count = summary.get('total', 0)
                active_count = summary.get('active', 0)
            
            return True, f"Successfully authenticated to Wazuh {version}\nAgents: {agent_count} (Active: {active_count})"
        elif auth_resp.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {auth_resp.status_code}: {auth_resp.text[:200]}"
            
    except Exception as e:
        return False, f"Wazuh error: {e}"

