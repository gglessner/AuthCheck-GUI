# Raritan PDU Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Raritan PDU (Power)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.100"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / raritan (default). HTTPS: 443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Raritan intelligent PDU.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
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
        
        # Raritan PDU JSON-RPC login
        login_url = f"{base_url}/bulk/a"
        headers = {"Content-Type": "application/json"}
        login_data = {
            "jsonrpc": "2.0",
            "method": "login",
            "params": {
                "user": username,
                "password": password
            },
            "id": 1
        }
        
        import json
        response = session.post(login_url, data=json.dumps(login_data), headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("result") and not data.get("error"):
                # Get PDU info
                info_data = {
                    "jsonrpc": "2.0",
                    "method": "get",
                    "params": ["pdu.model"],
                    "id": 2
                }
                
                info_resp = session.post(login_url, data=json.dumps(info_data), headers=headers, timeout=10)
                
                model = "Raritan PDU"
                if info_resp.status_code == 200:
                    info_result = info_resp.json()
                    if info_result.get("result"):
                        model = info_result.get("result", "Raritan PDU")
                
                return True, f"Successfully authenticated to {model} at {host}"
            elif data.get("error"):
                return False, f"Authentication failed: {data.get('error', {}).get('message', 'Invalid credentials')}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Raritan PDU error: {e}"

