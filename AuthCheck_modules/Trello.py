# Trello Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Trello (Collaboration)"

form_fields = [
    {"name": "api_key", "type": "text", "label": "API Key"},
    {"name": "token", "type": "password", "label": "Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API Key from trello.com/power-ups/admin. Generate token from the key page."},
]


def authenticate(form_data):
    """Attempt to authenticate to Trello."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    api_key = form_data.get('api_key', '').strip()
    token = form_data.get('token', '').strip()
    
    if not api_key:
        return False, "API Key is required"
    if not token:
        return False, "Token is required"
    
    try:
        params = {'key': api_key, 'token': token}
        
        # Get current member
        response = requests.get("https://api.trello.com/1/members/me",
                               params=params, timeout=15)
        
        if response.status_code == 200:
            member = response.json()
            username = member.get('username', 'unknown')
            full_name = member.get('fullName', 'unknown')
            
            # Get boards
            boards_resp = requests.get("https://api.trello.com/1/members/me/boards",
                                      params=params, timeout=10)
            board_count = 0
            board_names = []
            if boards_resp.status_code == 200:
                boards = boards_resp.json()
                board_count = len(boards)
                board_names = [b['name'] for b in boards[:3]]
            
            # Get organizations
            orgs_resp = requests.get("https://api.trello.com/1/members/me/organizations",
                                    params=params, timeout=10)
            org_count = 0
            if orgs_resp.status_code == 200:
                org_count = len(orgs_resp.json())
            
            return True, f"Successfully authenticated to Trello\nUser: {full_name} (@{username})\nBoards: {board_count}\nOrganizations: {org_count}\nSample Boards: {', '.join(board_names) if board_names else 'none'}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Trello error: {e}"

