# Monday.com Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Monday.com (Collaboration)"

form_fields = [
    {"name": "api_token", "type": "password", "label": "API Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API token from Avatar > Developers > My Access Tokens."},
]


def authenticate(form_data):
    """Attempt to authenticate to Monday.com."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    api_token = form_data.get('api_token', '').strip()
    
    if not api_token:
        return False, "API Token is required"
    
    try:
        headers = {
            'Authorization': api_token,
            'Content-Type': 'application/json'
        }
        
        # GraphQL query to get account and user info
        query = """
        query {
            me {
                name
                email
            }
            account {
                name
                plan {
                    tier
                }
            }
            boards(limit: 100) {
                id
            }
        }
        """
        
        response = requests.post(
            "https://api.monday.com/v2",
            headers=headers,
            json={'query': query},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            
            if 'errors' in response.json():
                errors = response.json()['errors']
                return False, f"API Error: {errors[0].get('message', 'Unknown error')}"
            
            me = data.get('me', {})
            account = data.get('account', {})
            boards = data.get('boards', [])
            
            user_name = me.get('name', 'unknown')
            email = me.get('email', 'unknown')
            account_name = account.get('name', 'unknown')
            plan = account.get('plan', {}).get('tier', 'unknown')
            
            return True, f"Successfully authenticated to Monday.com\nUser: {user_name} ({email})\nAccount: {account_name}\nPlan: {plan}\nBoards: {len(boards)}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Monday.com error: {e}"

