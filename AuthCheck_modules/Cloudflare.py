# Cloudflare Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Cloudflare (Cloud)"

form_fields = [
    {"name": "api_token", "type": "password", "label": "API Token"},
    {"name": "api_key", "type": "password", "label": "Global API Key (Legacy)"},
    {"name": "email", "type": "text", "label": "Email (for Global API Key)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API Token from My Profile > API Tokens (preferred). Global API Key from Overview page."},
]


def authenticate(form_data):
    """Attempt to authenticate to Cloudflare."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    api_token = form_data.get('api_token', '').strip()
    api_key = form_data.get('api_key', '').strip()
    email = form_data.get('email', '').strip()
    
    try:
        if api_token:
            headers = {
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
            }
        elif api_key and email:
            headers = {
                'X-Auth-Email': email,
                'X-Auth-Key': api_key,
                'Content-Type': 'application/json'
            }
        else:
            return False, "API Token or Global API Key with Email required"
        
        # Verify token
        response = requests.get("https://api.cloudflare.com/client/v4/user/tokens/verify",
                               headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                # Get user info
                user_resp = requests.get("https://api.cloudflare.com/client/v4/user",
                                        headers=headers, timeout=10)
                user_email = 'unknown'
                if user_resp.status_code == 200 and user_resp.json().get('success'):
                    user_email = user_resp.json().get('result', {}).get('email', 'unknown')
                
                # Get zone count
                zones_resp = requests.get("https://api.cloudflare.com/client/v4/zones",
                                         headers=headers, timeout=10)
                zone_count = 0
                if zones_resp.status_code == 200 and zones_resp.json().get('success'):
                    zone_count = zones_resp.json().get('result_info', {}).get('total_count', 0)
                
                # Get account info
                accounts_resp = requests.get("https://api.cloudflare.com/client/v4/accounts",
                                            headers=headers, timeout=10)
                account_count = 0
                if accounts_resp.status_code == 200 and accounts_resp.json().get('success'):
                    account_count = len(accounts_resp.json().get('result', []))
                
                return True, f"Successfully authenticated to Cloudflare\nUser: {user_email}\nAccounts: {account_count}\nZones: {zone_count}"
            else:
                errors = data.get('errors', [])
                error_msg = errors[0].get('message', 'Unknown error') if errors else 'Token invalid'
                return False, f"Authentication failed: {error_msg}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Cloudflare error: {e}"

