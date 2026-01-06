# ClickUp Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "ClickUp (Collaboration)"

form_fields = [
    {"name": "api_token", "type": "password", "label": "API Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Personal API token from Settings > Apps > API Token."},
]


def authenticate(form_data):
    """Attempt to authenticate to ClickUp."""
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
        
        # Get user info
        response = requests.get(
            "https://api.clickup.com/api/v2/user",
            headers=headers, timeout=15
        )
        
        if response.status_code == 200:
            user = response.json().get('user', {})
            username = user.get('username', 'unknown')
            email = user.get('email', 'unknown')
            
            # Get teams (workspaces)
            teams_resp = requests.get(
                "https://api.clickup.com/api/v2/team",
                headers=headers, timeout=10
            )
            team_count = 0
            team_names = []
            if teams_resp.status_code == 200:
                teams = teams_resp.json().get('teams', [])
                team_count = len(teams)
                team_names = [t['name'] for t in teams[:3]]
            
            return True, f"Successfully authenticated to ClickUp\nUser: {username} ({email})\nWorkspaces: {team_count}\nSample: {', '.join(team_names) if team_names else 'none'}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"ClickUp error: {e}"

