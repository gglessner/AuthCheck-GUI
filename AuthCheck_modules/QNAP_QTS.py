# QNAP QTS Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "QNAP QTS (NAS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.100"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "8080"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / admin (default). HTTP: 8080, HTTPS: 443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to QNAP QTS.
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
        
        # QTS API login
        login_url = f"{base_url}/cgi-bin/authLogin.cgi"
        
        # Encode password in base64
        import base64
        encoded_pwd = base64.b64encode(password.encode()).decode()
        
        login_data = {
            "user": username,
            "pwd": encoded_pwd
        }
        
        response = session.post(login_url, data=login_data, timeout=15)
        
        if response.status_code == 200:
            # Check for authSid in response
            if "authSid" in response.text or "QTS" in response.text:
                import re
                
                # Get NAS info
                info_url = f"{base_url}/cgi-bin/management/manaRequest.cgi"
                info_data = {"subfunc": "sysinfo", "sysinfo": "detail"}
                
                info_resp = session.post(info_url, data=info_data, timeout=10)
                
                model = "QNAP NAS"
                firmware = "unknown"
                if info_resp.status_code == 200:
                    model_match = re.search(r'model["\s:]+([^"<\s,]+)', info_resp.text, re.IGNORECASE)
                    if model_match:
                        model = model_match.group(1)
                    fw_match = re.search(r'version["\s:]+([^"<\s,]+)', info_resp.text, re.IGNORECASE)
                    if fw_match:
                        firmware = fw_match.group(1)
                
                return True, f"Successfully authenticated to {model}\nFirmware: {firmware}"
            elif "error" in response.text.lower() or "failed" in response.text.lower():
                return False, "Authentication failed: Invalid credentials"
        
        # Try alternative login method
        login_url = f"{base_url}/cgi-bin/authLogin.cgi"
        params = {
            "user": username,
            "pwd": password
        }
        
        response = session.get(login_url, params=params, timeout=15)
        
        if response.status_code == 200 and "authSid" in response.text:
            return True, f"Successfully authenticated to QNAP at {host}"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"QNAP error: {e}"

