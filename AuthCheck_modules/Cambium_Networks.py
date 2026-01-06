# Cambium Networks Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Cambium Networks (Wireless)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.0.1"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "platform", "type": "combo", "label": "Platform",
     "options": ["cnMaestro", "cnPilot", "ePMP", "PMP", "Standalone"]},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "client_id", "type": "text", "label": "Client ID (cnMaestro API)"},
    {"name": "client_secret", "type": "password", "label": "Client Secret"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / admin. cnMaestro Cloud: cloud.cambiumnetworks.com"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Cambium Networks device or cloud.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    platform = form_data.get('platform', 'Standalone')
    use_https = form_data.get('use_https', True)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    scheme = "https" if use_https else "http"
    base_url = f"{scheme}://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        if platform == "cnMaestro":
            # cnMaestro API
            if client_id and client_secret:
                token_url = f"{base_url}/api/v1/access/token"
                token_data = {
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret
                }
                
                response = session.post(token_url, data=token_data, timeout=15)
                
                if response.status_code == 200:
                    token = response.json().get('access_token')
                    if token:
                        # Get device count
                        headers = {"Authorization": f"Bearer {token}"}
                        devices_resp = session.get(f"{base_url}/api/v1/devices", 
                                                   headers=headers, timeout=10)
                        device_count = 0
                        if devices_resp.status_code == 200:
                            device_count = len(devices_resp.json().get('data', []))
                        
                        return True, f"Successfully authenticated to cnMaestro\nDevices: {device_count}"
            else:
                # Web login
                login_url = f"{base_url}/api/v1/login"
                login_data = {"username": username, "password": password}
                
                response = session.post(login_url, json=login_data, timeout=15)
                
                if response.status_code == 200:
                    return True, f"Successfully authenticated to cnMaestro at {host}"
                    
        elif platform in ["ePMP", "PMP", "cnPilot"]:
            # Device web interface
            login_url = f"{base_url}/cgi-bin/luci"
            login_data = {
                "luci_username": username,
                "luci_password": password
            }
            
            response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
            
            if response.status_code == 200 and "logout" in response.text.lower():
                return True, f"Successfully authenticated to {platform} at {host}"
                
        else:  # Standalone
            login_url = f"{base_url}/api/login"
            login_data = {"username": username, "password": password}
            
            response = session.post(login_url, json=login_data, timeout=15)
            
            if response.status_code == 200:
                return True, f"Successfully authenticated to Cambium device at {host}"
        
        if response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        return False, f"Authentication failed: HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Cambium error: {e}"

