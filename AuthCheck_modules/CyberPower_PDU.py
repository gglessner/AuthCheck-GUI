# CyberPower PDU/UPS Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "CyberPower PDU/UPS (Power)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.100"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "cyber"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "cyber / cyber (default). HTTPS: 443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to CyberPower PDU/UPS network card.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
    use_https = form_data.get('use_https', True)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    scheme = "https" if use_https else "http"
    base_url = f"{scheme}://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # CyberPower RMCARD login
        login_url = f"{base_url}/agent/login"
        login_data = {
            "username": username,
            "password": password
        }
        
        headers = {"Content-Type": "application/json"}
        import json
        
        response = session.post(login_url, data=json.dumps(login_data), headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("token") or data.get("success"):
                # Get device info
                info_url = f"{base_url}/agent/device/info"
                info_resp = session.get(info_url, headers=headers, timeout=10)
                
                model = "CyberPower"
                if info_resp.status_code == 200:
                    model = info_resp.json().get("model", "CyberPower")
                
                return True, f"Successfully authenticated to {model} at {host}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        # Try form login
        login_url = f"{base_url}/login.htm"
        login_data = {
            "Username": username,
            "Password": password
        }
        
        response = session.post(login_url, data=login_data, timeout=15)
        
        if response.status_code == 200 and "logout" in response.text.lower():
            return True, f"Successfully authenticated to CyberPower at {host}"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"CyberPower error: {e}"

