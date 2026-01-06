# Kyocera Printer Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Kyocera Printer (Printer)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.100"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "Admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Admin / Admin (ECOSYS). Command Center RX: 80/443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Kyocera Printer Command Center RX.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', True)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    scheme = "https" if use_https else "http"
    base_url = f"{scheme}://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # Get device info
        info_url = f"{base_url}/startwlm/Start_Wlm.htm"
        info_resp = session.get(info_url, timeout=10)
        
        model = "Kyocera Printer"
        if info_resp.status_code == 200:
            import re
            match = re.search(r'ECOSYS\s+(\w+)', info_resp.text, re.IGNORECASE)
            if match:
                model = f"ECOSYS {match.group(1)}"
        
        # Kyocera Command Center login
        login_url = f"{base_url}/startwlm/Start_Wlm.htm"
        login_data = {
            "okhtmfile": "/index.htm",
            "username": username,
            "password": password,
            "func": "authLogin"
        }
        
        response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
        
        if response.status_code == 200:
            if "logout" in response.text.lower() or "admin" in response.text.lower():
                return True, f"Successfully authenticated to {model} at {host}"
            elif "error" in response.text.lower() or "failed" in response.text.lower():
                return False, "Authentication failed: Invalid credentials"
        
        # Try alternative (HyPAS)
        login_url = f"{base_url}/ws/km-wsdl/setting/localauth"
        login_data = f'''<?xml version="1.0" encoding="UTF-8"?>
        <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope">
            <SOAP-ENV:Body>
                <kmauth:Login xmlns:kmauth="http://www.kyoceramita.com/ws/km-wsdl/setting/localauth">
                    <kmauth:UserName>{username}</kmauth:UserName>
                    <kmauth:Password>{password}</kmauth:Password>
                </kmauth:Login>
            </SOAP-ENV:Body>
        </SOAP-ENV:Envelope>'''
        
        headers = {"Content-Type": "application/soap+xml"}
        response = session.post(login_url, data=login_data, headers=headers, timeout=15)
        
        if response.status_code == 200 and "success" in response.text.lower():
            return True, f"Successfully authenticated to {model} at {host}"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Kyocera error: {e}"

