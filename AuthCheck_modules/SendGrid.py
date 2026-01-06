# SendGrid Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "SendGrid (Email)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API Key from Settings > API Keys. Starts with 'SG.'"},
]


def authenticate(form_data):
    """Attempt to authenticate to SendGrid."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    api_key = form_data.get('api_key', '').strip()
    
    if not api_key:
        return False, "API Key is required"
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Get user profile
        response = requests.get("https://api.sendgrid.com/v3/user/profile",
                               headers=headers, timeout=15)
        
        if response.status_code == 200:
            profile = response.json()
            company = profile.get('company', 'unknown')
            email = profile.get('email', 'unknown')
            
            # Get account details
            account_resp = requests.get("https://api.sendgrid.com/v3/user/account",
                                       headers=headers, timeout=10)
            account_type = 'unknown'
            if account_resp.status_code == 200:
                account_type = account_resp.json().get('type', 'unknown')
            
            # Get API key scopes
            scopes_resp = requests.get("https://api.sendgrid.com/v3/scopes",
                                      headers=headers, timeout=10)
            scope_count = 0
            if scopes_resp.status_code == 200:
                scope_count = len(scopes_resp.json().get('scopes', []))
            
            return True, f"Successfully authenticated to SendGrid\nCompany: {company}\nEmail: {email}\nAccount Type: {account_type}\nAPI Scopes: {scope_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API key"
        elif response.status_code == 403:
            return False, "Authentication failed: Insufficient permissions"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"SendGrid error: {e}"

