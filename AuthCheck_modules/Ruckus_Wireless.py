# Ruckus Wireless Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Ruckus Wireless (Wireless)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.0.1"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "controller_type", "type": "combo", "label": "Controller Type",
     "options": ["SmartZone", "ZoneDirector", "Unleashed", "Standalone AP"]},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / admin (ZD), super / sp-admin (SZ). HTTPS: 443, HTTP: 80"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Ruckus Wireless controller.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    controller_type = form_data.get('controller_type', 'ZoneDirector')
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
        
        if controller_type == "SmartZone":
            # SmartZone API
            login_url = f"{base_url}/wsg/api/public/v11_1/serviceTicket"
            login_data = {
                "username": username,
                "password": password
            }
            
            response = session.post(login_url, json=login_data, timeout=15)
            
            if response.status_code == 200:
                ticket = response.json().get('serviceTicket')
                if ticket:
                    # Get system info
                    headers = {"Authorization": f"Bearer {ticket}"}
                    info_resp = session.get(f"{base_url}/wsg/api/public/v11_1/system/summary", 
                                           headers=headers, timeout=10)
                    
                    version = "unknown"
                    ap_count = 0
                    if info_resp.status_code == 200:
                        info = info_resp.json()
                        version = info.get('version', 'unknown')
                        ap_count = info.get('totalAPs', 0)
                    
                    return True, f"Successfully authenticated to SmartZone\nVersion: {version}\nAPs: {ap_count}"
                    
        elif controller_type == "ZoneDirector":
            # ZoneDirector web login
            login_url = f"{base_url}/admin/login.jsp"
            login_data = {
                "username": username,
                "password": password,
                "ok": "Log In"
            }
            
            response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
            
            if "logout" in response.text.lower() or "dashboard" in response.text.lower():
                return True, f"Successfully authenticated to ZoneDirector at {host}"
            elif "invalid" in response.text.lower() or "failed" in response.text.lower():
                return False, "Authentication failed: Invalid credentials"
                
        elif controller_type == "Unleashed":
            # Unleashed API
            login_url = f"{base_url}/api/v1/login"
            login_data = {
                "username": username,
                "password": password
            }
            
            response = session.post(login_url, json=login_data, timeout=15)
            
            if response.status_code == 200:
                return True, f"Successfully authenticated to Ruckus Unleashed at {host}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
                
        else:  # Standalone AP
            login_url = f"{base_url}/admin/login.jsp"
            login_data = {
                "username": username,
                "password": password
            }
            
            response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
            
            if response.status_code == 200 and "logout" in response.text.lower():
                return True, f"Successfully authenticated to Ruckus AP at {host}"
        
        return False, f"Authentication failed or unsupported controller type"
            
    except Exception as e:
        return False, f"Ruckus error: {e}"

