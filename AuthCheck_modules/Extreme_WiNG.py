# Extreme Networks WiNG Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Extreme Networks WiNG (Wireless)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.0.1"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "controller_type", "type": "combo", "label": "Type",
     "options": ["WiNG Controller", "Virtual Controller", "Standalone AP", "ExtremeCloud IQ"]},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "api_key", "type": "password", "label": "API Key (ExtremeCloud)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / admin123. ExtremeCloud IQ: extremecloudiq.com"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Extreme Networks WiNG.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    controller_type = form_data.get('controller_type', 'WiNG Controller')
    use_https = form_data.get('use_https', True)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    api_key = form_data.get('api_key', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host and controller_type != "ExtremeCloud IQ":
        return False, "Host is required"
    
    scheme = "https" if use_https else "http"
    base_url = f"{scheme}://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        if controller_type == "ExtremeCloud IQ":
            # ExtremeCloud IQ API
            cloud_url = "https://api.extremecloudiq.com"
            
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            
            if not api_key:
                # Try login
                login_url = f"{cloud_url}/login"
                login_data = {
                    "username": username,
                    "password": password
                }
                response = session.post(login_url, json=login_data, timeout=15)
                
                if response.status_code == 200:
                    token = response.json().get('access_token')
                    if token:
                        headers = {"Authorization": f"Bearer {token}"}
            
            # Get device list
            devices_url = f"{cloud_url}/devices"
            response = session.get(devices_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                devices = response.json()
                count = len(devices.get('data', []))
                return True, f"Successfully authenticated to ExtremeCloud IQ\nDevices: {count}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
                
        else:
            # WiNG controller/AP web interface
            login_url = f"{base_url}/rest/v1/act/login"
            login_data = {
                "username": username,
                "password": password
            }
            
            response = session.post(login_url, json=login_data, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('token') or data.get('session'):
                    return True, f"Successfully authenticated to WiNG at {host}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            
            # Try legacy login
            login_url = f"{base_url}/login.html"
            login_data = {
                "username": username,
                "password": password
            }
            
            response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
            
            if response.status_code == 200 and "logout" in response.text.lower():
                return True, f"Successfully authenticated to WiNG device at {host}"
            
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Extreme WiNG error: {e}"

