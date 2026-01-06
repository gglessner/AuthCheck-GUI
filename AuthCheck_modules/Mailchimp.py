# Mailchimp Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Mailchimp (Email)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API key from Account > Extras > API keys. Format: xxx-usX (server suffix)."},
]


def authenticate(form_data):
    """Attempt to authenticate to Mailchimp."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    api_key = form_data.get('api_key', '').strip()
    
    if not api_key:
        return False, "API Key is required"
    
    # Extract datacenter from API key
    if '-' not in api_key:
        return False, "Invalid API key format. Should end with -usX (datacenter)"
    
    datacenter = api_key.split('-')[-1]
    
    try:
        auth = HTTPBasicAuth('anystring', api_key)
        
        # Get account info
        response = requests.get(
            f"https://{datacenter}.api.mailchimp.com/3.0/",
            auth=auth, timeout=15
        )
        
        if response.status_code == 200:
            account = response.json()
            account_name = account.get('account_name', 'unknown')
            email = account.get('email', 'unknown')
            total_subscribers = account.get('total_subscribers', 0)
            
            # Get list count
            lists_resp = requests.get(
                f"https://{datacenter}.api.mailchimp.com/3.0/lists?count=1",
                auth=auth, timeout=10
            )
            list_count = 0
            if lists_resp.status_code == 200:
                list_count = lists_resp.json().get('total_items', 0)
            
            # Get campaign count
            campaigns_resp = requests.get(
                f"https://{datacenter}.api.mailchimp.com/3.0/campaigns?count=1",
                auth=auth, timeout=10
            )
            campaign_count = 0
            if campaigns_resp.status_code == 200:
                campaign_count = campaigns_resp.json().get('total_items', 0)
            
            return True, f"Successfully authenticated to Mailchimp\nAccount: {account_name}\nEmail: {email}\nTotal Subscribers: {total_subscribers}\nLists: {list_count}\nCampaigns: {campaign_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API key"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Mailchimp error: {e}"

