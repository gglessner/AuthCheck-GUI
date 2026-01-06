# Zscaler ZPA Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Zscaler ZPA (ZTNA)"

form_fields = [
    {"name": "cloud", "type": "combo", "label": "Cloud",
     "options": ["zscaler.net", "zscalerone.net", "zscalertwo.net", "zscloud.net", "zscalerthree.net"]},
    {"name": "client_id", "type": "text", "label": "Client ID"},
    {"name": "client_secret", "type": "password", "label": "Client Secret"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "ZPA Admin API credentials"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Zscaler ZPA API.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    cloud = form_data.get('cloud', 'zscaler.net')
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '').strip()
    
    if not client_id:
        return False, "Client ID is required"
    if not client_secret:
        return False, "Client Secret is required"
    
    try:
        session = requests.Session()
        
        # ZPA OAuth token
        token_url = f"https://config.private.{cloud}/signin"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token_data = {
            "client_id": client_id,
            "client_secret": client_secret
        }
        
        response = session.post(token_url, data=token_data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("access_token"):
                token = data.get("access_token")
                
                # Get customer info
                customer_url = f"https://config.private.{cloud}/mgmtconfig/v1/admin/customers"
                headers["Authorization"] = f"Bearer {token}"
                
                cust_resp = session.get(customer_url, headers=headers, timeout=10)
                
                return True, f"Successfully authenticated to Zscaler ZPA\nCloud: {cloud}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Zscaler ZPA error: {e}"

