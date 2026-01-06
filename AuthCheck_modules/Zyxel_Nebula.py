# Zyxel Nebula Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Zyxel Nebula (Wireless)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.1"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "mode", "type": "combo", "label": "Mode",
     "options": ["Nebula Cloud", "Standalone AP", "NCC Controller"]},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "api_key", "type": "password", "label": "API Key (Nebula)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Standalone: admin / 1234. Nebula Cloud: nebula.zyxel.com"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Zyxel Nebula or device.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    mode = form_data.get('mode', 'Standalone AP')
    use_https = form_data.get('use_https', True)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    api_key = form_data.get('api_key', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host and mode != "Nebula Cloud":
        return False, "Host is required"
    
    scheme = "https" if use_https else "http"
    base_url = f"{scheme}://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        if mode == "Nebula Cloud":
            # Nebula Cloud API
            cloud_url = "https://api.nebula.zyxel.com"
            
            headers = {}
            if api_key:
                headers['X-Zyxel-Auth-Key'] = api_key
            
            response = session.get(f"{cloud_url}/v1/organizations", 
                                   headers=headers, timeout=15)
            
            if response.status_code == 200:
                orgs = response.json()
                org_count = len(orgs.get('data', []))
                return True, f"Successfully authenticated to Zyxel Nebula Cloud\nOrganizations: {org_count}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid API key"
            else:
                return False, f"HTTP {response.status_code}"
                
        elif mode == "NCC Controller":
            # Nebula Control Center
            login_url = f"{base_url}/api/v1/auth/login"
            login_data = {
                "username": username,
                "password": password
            }
            
            response = session.post(login_url, json=login_data, timeout=15)
            
            if response.status_code == 200:
                return True, f"Successfully authenticated to NCC at {host}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
                
        else:  # Standalone AP
            login_url = f"{base_url}/weblogin.cgi"
            login_data = {
                "username": username,
                "password": password
            }
            
            response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
            
            if response.status_code == 200:
                if "logout" in response.text.lower() or "status" in response.text.lower():
                    return True, f"Successfully authenticated to Zyxel AP at {host}"
                elif "incorrect" in response.text.lower() or "failed" in response.text.lower():
                    return False, "Authentication failed: Invalid credentials"
            
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Zyxel error: {e}"

