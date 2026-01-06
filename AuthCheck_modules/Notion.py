# Notion Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Notion (Collaboration)"

form_fields = [
    {"name": "integration_token", "type": "password", "label": "Integration Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Internal integration token from notion.so/my-integrations. Starts with 'secret_'."},
]


def authenticate(form_data):
    """Attempt to authenticate to Notion."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    integration_token = form_data.get('integration_token', '').strip()
    
    if not integration_token:
        return False, "Integration Token is required"
    
    try:
        headers = {
            'Authorization': f'Bearer {integration_token}',
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json'
        }
        
        # Get bot user info
        response = requests.get("https://api.notion.com/v1/users/me",
                               headers=headers, timeout=15)
        
        if response.status_code == 200:
            bot = response.json()
            bot_name = bot.get('name', 'unknown')
            bot_type = bot.get('type', 'unknown')
            
            # Search for pages (to verify access)
            search_resp = requests.post("https://api.notion.com/v1/search",
                                       headers=headers,
                                       json={'page_size': 10},
                                       timeout=10)
            page_count = 0
            if search_resp.status_code == 200:
                results = search_resp.json().get('results', [])
                page_count = len(results)
            
            # Get users
            users_resp = requests.get("https://api.notion.com/v1/users",
                                     headers=headers, timeout=10)
            user_count = 0
            if users_resp.status_code == 200:
                user_count = len(users_resp.json().get('results', []))
            
            return True, f"Successfully authenticated to Notion\nBot: {bot_name}\nType: {bot_type}\nAccessible Pages: {page_count}\nWorkspace Users: {user_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Notion error: {e}"

