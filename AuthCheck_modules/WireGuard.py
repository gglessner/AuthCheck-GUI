# WireGuard Web Interface Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "WireGuard Web UI (VPN)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.1"},
    {"name": "port", "type": "text", "label": "Port", "default": "51821"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "wg-easy UI: 51821. VPN: 51820/UDP"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to WireGuard web UI (wg-easy).
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '51821').strip()
    use_https = form_data.get('use_https', False)
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    scheme = "https" if use_https else "http"
    base_url = f"{scheme}://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # wg-easy session auth
        login_url = f"{base_url}/api/session"
        login_data = {"password": password}
        headers = {"Content-Type": "application/json"}
        
        import json
        response = session.post(login_url, data=json.dumps(login_data), headers=headers, timeout=15)
        
        if response.status_code == 200 or response.status_code == 204:
            # Get clients info
            clients_url = f"{base_url}/api/wireguard/client"
            clients_resp = session.get(clients_url, timeout=10)
            
            client_count = 0
            if clients_resp.status_code == 200:
                client_count = len(clients_resp.json())
            
            return True, f"Successfully authenticated to WireGuard UI at {host}\nClients: {client_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid password"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"WireGuard error: {e}"

