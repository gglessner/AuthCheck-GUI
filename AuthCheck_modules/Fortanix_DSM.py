# Fortanix Data Security Manager Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Fortanix DSM (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "Fortanix DSM Host", "default": "sdkms.fortanix.com"},
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "username", "type": "text", "label": "Username (Alternative)"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Cloud or on-prem. API key from Apps > New App. HSM-grade key management."},
]


def authenticate(form_data):
    """Attempt to authenticate to Fortanix DSM."""
    try:
        import requests
        import base64
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', 'sdkms.fortanix.com').strip()
    api_key = form_data.get('api_key', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Fortanix DSM Host is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        if api_key:
            # API key authentication
            headers = {
                'Authorization': f'Basic {base64.b64encode(api_key.encode()).decode()}',
                'Content-Type': 'application/json'
            }
            
            # Authenticate session
            auth_resp = session.post(
                f"{host}/sys/v1/session/auth",
                headers=headers,
                timeout=15
            )
            
            if auth_resp.status_code == 200:
                # Get account info
                acct_resp = session.get(
                    f"{host}/sys/v1/session/me",
                    headers=headers,
                    timeout=10
                )
                
                if acct_resp.status_code == 200:
                    me = acct_resp.json()
                    account_name = me.get('account_name', 'unknown')
                    user_email = me.get('user_email', 'API Key')
                    
                    # Get security objects count
                    sobjects_resp = session.get(
                        f"{host}/crypto/v1/keys?limit=1",
                        headers=headers,
                        timeout=10
                    )
                    key_count = 0
                    if sobjects_resp.status_code == 200:
                        key_count = len(sobjects_resp.json())
                    
                    return True, f"Successfully authenticated to Fortanix DSM\nHost: {host}\nAccount: {account_name}\nUser: {user_email}\nKeys: {key_count}+"
                
                return True, f"Successfully authenticated to Fortanix DSM\nHost: {host}"
            elif auth_resp.status_code == 401:
                return False, "Authentication failed: Invalid API key"
                
        elif username and password:
            # Username/password authentication
            auth_resp = session.post(
                f"{host}/sys/v1/session/auth",
                auth=(username, password),
                timeout=15
            )
            
            if auth_resp.status_code == 200:
                return True, f"Successfully authenticated to Fortanix DSM\nHost: {host}\nUser: {username}"
            elif auth_resp.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
        else:
            return False, "API Key or Username/Password required"
        
        return False, f"Could not authenticate to {host}"
            
    except Exception as e:
        return False, f"Fortanix DSM error: {e}"

