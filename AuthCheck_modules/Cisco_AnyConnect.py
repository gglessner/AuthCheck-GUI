# Cisco AnyConnect VPN Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Cisco AnyConnect (VPN)"

form_fields = [
    {"name": "host", "type": "text", "label": "VPN Host", "default": "vpn.example.com"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "group", "type": "text", "label": "Group/Tunnel-Group"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "ASA/FTD AnyConnect. HTTPS: 443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Cisco AnyConnect VPN.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
    group = form_data.get('group', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    base_url = f"https://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # AnyConnect XML login
        login_url = f"{base_url}/+webvpn+/index.html"
        
        login_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
        <config-auth client="vpn" type="auth-request">
            <version who="vpn">4.0</version>
            <device-id>test-device</device-id>
            <group-access>{base_url}/{group}</group-access>
            <auth>
                <username>{username}</username>
                <password>{password}</password>
            </auth>
        </config-auth>'''
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = session.post(login_url, data=login_xml, headers=headers, timeout=15)
        
        if response.status_code == 200:
            if "auth-success" in response.text.lower() or "session-token" in response.text.lower():
                return True, f"Successfully authenticated to Cisco AnyConnect at {host}"
            elif "auth-failed" in response.text.lower() or "invalid" in response.text.lower():
                return False, "Authentication failed: Invalid credentials"
        
        # Try webvpn login
        login_url = f"{base_url}/+webvpn+/index.html"
        login_data = {
            "username": username,
            "password": password,
            "group_list": group
        }
        
        response = session.post(login_url, data=login_data, timeout=15)
        
        if response.status_code == 200 and "logout" in response.text.lower():
            return True, f"Successfully authenticated to Cisco AnyConnect at {host}"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Cisco AnyConnect error: {e}"

