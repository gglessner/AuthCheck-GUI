# ArcSight Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "ArcSight (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "ArcSight Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "8443"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: admin/password. ESM Console port 8443. Micro Focus OpenText."},
]


def authenticate(form_data):
    """Attempt to authenticate to ArcSight."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8443').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "ArcSight Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        base_url = f"https://{host}:{port}"
        
        # Login to get auth token
        login_data = f"""<?xml version="1.0" encoding="UTF-8"?>
        <ns1:login xmlns:ns1="http://ws.v1.service.resource.manager.product.arcsight.com/loginService/">
            <ns1:username>{username}</ns1:username>
            <ns1:password>{password}</ns1:password>
        </ns1:login>"""
        
        headers = {
            'Content-Type': 'application/xml',
            'Accept': 'application/xml'
        }
        
        response = requests.post(
            f"{base_url}/www/manager-service/services/LoginService",
            data=login_data,
            headers=headers,
            verify=verify_ssl,
            timeout=15
        )
        
        if response.status_code == 200:
            if 'authToken' in response.text or 'sessionId' in response.text:
                return True, f"Successfully authenticated to ArcSight ESM\nHost: {host}:{port}\nUser: {username}"
            elif 'fault' in response.text.lower() or 'error' in response.text.lower():
                return False, "Authentication failed: Invalid credentials"
            else:
                return True, f"Connected to ArcSight ESM\nHost: {host}:{port}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"ArcSight error: {e}"

