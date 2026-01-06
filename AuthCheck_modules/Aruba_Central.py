# Aruba Central Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Aruba Central (Wireless)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "apigw-prod2.central.arubanetworks.com"},
    {"name": "client_id", "type": "text", "label": "Client ID (API)"},
    {"name": "client_secret", "type": "password", "label": "Client Secret"},
    {"name": "customer_id", "type": "text", "label": "Customer ID"},
    {"name": "username", "type": "text", "label": "Username (for token)"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Cloud-based. Get API credentials from Aruba Central > Account > API Gateway"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Aruba Central.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '')
    customer_id = form_data.get('customer_id', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', True)
    
    if not host:
        return False, "Host is required"
    if not client_id:
        return False, "Client ID is required"
    
    base_url = f"https://{host}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # OAuth token request
        token_url = f"{base_url}/oauth2/token"
        token_data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
        
        if username and password:
            token_data["grant_type"] = "password"
            token_data["username"] = username
            token_data["password"] = password
        
        response = session.post(token_url, data=token_data, timeout=15)
        
        if response.status_code == 200:
            token_info = response.json()
            access_token = token_info.get('access_token')
            
            if access_token:
                # Get account info
                headers = {"Authorization": f"Bearer {access_token}"}
                
                # List APs
                aps_url = f"{base_url}/monitoring/v2/aps"
                if customer_id:
                    headers["X-Customer-Id"] = customer_id
                
                aps_resp = session.get(aps_url, headers=headers, timeout=10)
                
                ap_count = 0
                if aps_resp.status_code == 200:
                    ap_data = aps_resp.json()
                    ap_count = ap_data.get('count', len(ap_data.get('aps', [])))
                
                return True, f"Successfully authenticated to Aruba Central\nAccess Points: {ap_count}"
            else:
                return False, "No access token received"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Aruba Central error: {e}"

