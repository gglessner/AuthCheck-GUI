# Cloudflare Access/Zero Trust Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Cloudflare Access/ZTNA (ZTNA)"

form_fields = [
    {"name": "account_id", "type": "text", "label": "Account ID"},
    {"name": "api_email", "type": "text", "label": "API Email"},
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Cloudflare Zero Trust API credentials"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Cloudflare Access/Zero Trust.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    account_id = form_data.get('account_id', '').strip()
    api_email = form_data.get('api_email', '').strip()
    api_key = form_data.get('api_key', '').strip()
    
    if not account_id:
        return False, "Account ID is required"
    if not api_email:
        return False, "API Email is required"
    if not api_key:
        return False, "API Key is required"
    
    try:
        session = requests.Session()
        
        # Cloudflare API verify
        verify_url = "https://api.cloudflare.com/client/v4/user/tokens/verify"
        headers = {
            "X-Auth-Email": api_email,
            "X-Auth-Key": api_key,
            "Content-Type": "application/json"
        }
        
        response = session.get(verify_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                # Get Access apps
                apps_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/access/apps"
                apps_resp = session.get(apps_url, headers=headers, timeout=10)
                
                app_count = 0
                if apps_resp.status_code == 200:
                    apps_data = apps_resp.json()
                    if apps_data.get("success"):
                        app_count = len(apps_data.get("result", []))
                
                return True, f"Successfully authenticated to Cloudflare Access\nAccount: {account_id}\nApps: {app_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API credentials"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Cloudflare Access error: {e}"

