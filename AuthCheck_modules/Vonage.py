# Vonage (Nexmo) Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Vonage / Nexmo (PBX)"

form_fields = [
    {"name": "api_key", "type": "text", "label": "API Key"},
    {"name": "api_secret", "type": "password", "label": "API Secret"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API credentials from Vonage Dashboard > Settings."},
]


def authenticate(form_data):
    """Attempt to authenticate to Vonage."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    api_key = form_data.get('api_key', '').strip()
    api_secret = form_data.get('api_secret', '').strip()
    
    if not api_key:
        return False, "API Key is required"
    if not api_secret:
        return False, "API Secret is required"
    
    try:
        # Get account balance
        response = requests.get(
            f"https://rest.nexmo.com/account/get-balance?api_key={api_key}&api_secret={api_secret}",
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            balance = data.get('value', 0)
            
            # Get numbers
            numbers_resp = requests.get(
                f"https://rest.nexmo.com/account/numbers?api_key={api_key}&api_secret={api_secret}",
                timeout=10
            )
            number_count = 0
            if numbers_resp.status_code == 200:
                number_count = numbers_resp.json().get('count', 0)
            
            return True, f"Successfully authenticated to Vonage\nAPI Key: {api_key}\nBalance: ${balance:.2f}\nNumbers: {number_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            try:
                error = response.json().get('error-text', response.text[:200])
            except:
                error = response.text[:200]
            return False, f"HTTP {response.status_code}: {error}"
            
    except Exception as e:
        return False, f"Vonage error: {e}"

