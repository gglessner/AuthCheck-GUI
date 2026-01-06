# Twilio Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Twilio (PBX)"

form_fields = [
    {"name": "account_sid", "type": "text", "label": "Account SID"},
    {"name": "auth_token", "type": "password", "label": "Auth Token"},
    {"name": "api_key", "type": "text", "label": "API Key SID (Alternative)"},
    {"name": "api_secret", "type": "password", "label": "API Key Secret (Alternative)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Account SID/Auth Token from Console Dashboard. API Keys from Settings > API Keys."},
]


def authenticate(form_data):
    """Attempt to authenticate to Twilio."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    account_sid = form_data.get('account_sid', '').strip()
    auth_token = form_data.get('auth_token', '').strip()
    api_key = form_data.get('api_key', '').strip()
    api_secret = form_data.get('api_secret', '').strip()
    
    if not account_sid:
        return False, "Account SID is required"
    
    try:
        if api_key and api_secret:
            auth = HTTPBasicAuth(api_key, api_secret)
        elif auth_token:
            auth = HTTPBasicAuth(account_sid, auth_token)
        else:
            return False, "Auth Token or API Key/Secret required"
        
        # Get account info
        response = requests.get(f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}.json",
                               auth=auth, timeout=15)
        
        if response.status_code == 200:
            account = response.json()
            friendly_name = account.get('friendly_name', 'unknown')
            status = account.get('status', 'unknown')
            account_type = account.get('type', 'unknown')
            
            # Get phone number count
            numbers_resp = requests.get(
                f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/IncomingPhoneNumbers.json?PageSize=1",
                auth=auth, timeout=10)
            number_count = 0
            if numbers_resp.status_code == 200:
                # Check for total from response
                numbers_data = numbers_resp.json()
                if 'incoming_phone_numbers' in numbers_data:
                    # Need to get count another way
                    number_count = len(numbers_data.get('incoming_phone_numbers', []))
            
            return True, f"Successfully authenticated to Twilio\nAccount: {friendly_name}\nSID: {account_sid[:8]}...\nStatus: {status}\nType: {account_type}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Twilio error: {e}"

