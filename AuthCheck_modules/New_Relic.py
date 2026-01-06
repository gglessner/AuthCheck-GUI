# New Relic Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "New Relic (Monitoring)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key (User or License)"},
    {"name": "account_id", "type": "text", "label": "Account ID"},
    {"name": "region", "type": "combo", "label": "Region", "options": ["US", "EU"], "default": "US"},
    {"name": "key_type", "type": "combo", "label": "Key Type", "options": ["User API Key", "License Key", "Insights Insert Key"], "default": "User API Key"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "User API Key: NRAK-xxx. License Key: xxx-NRAL. Account ID from account settings."},
]


def authenticate(form_data):
    """Attempt to authenticate to New Relic."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    api_key = form_data.get('api_key', '').strip()
    account_id = form_data.get('account_id', '').strip()
    region = form_data.get('region', 'US')
    key_type = form_data.get('key_type', 'User API Key')
    
    if not api_key:
        return False, "API Key is required"
    
    try:
        if region == "EU":
            api_base = "https://api.eu.newrelic.com"
            graphql_url = "https://api.eu.newrelic.com/graphql"
        else:
            api_base = "https://api.newrelic.com"
            graphql_url = "https://api.newrelic.com/graphql"
        
        headers = {
            'Api-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        if key_type == "User API Key":
            # Use NerdGraph API
            query = """
            {
              actor {
                user {
                  email
                  name
                }
                accounts {
                  id
                  name
                }
              }
            }
            """
            response = requests.post(graphql_url, headers=headers, 
                                    json={'query': query}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    return False, f"GraphQL error: {data['errors'][0].get('message', 'Unknown error')}"
                
                actor = data.get('data', {}).get('actor', {})
                user = actor.get('user', {})
                accounts = actor.get('accounts', [])
                
                user_name = user.get('name', 'unknown')
                user_email = user.get('email', 'unknown')
                
                return True, f"Successfully authenticated to New Relic\nUser: {user_name} ({user_email})\nAccounts: {len(accounts)}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid API key"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:200]}"
        else:
            # For license keys, just validate format
            if key_type == "License Key" and 'NRAL' in api_key:
                return True, f"License key format validated\nRegion: {region}\nNote: License keys are for agent data ingest, not API access"
            elif key_type == "Insights Insert Key":
                return True, f"Insights Insert key provided\nRegion: {region}\nNote: Insert keys are for custom event data"
            else:
                return False, "Invalid key format for selected key type"
            
    except Exception as e:
        return False, f"New Relic error: {e}"

