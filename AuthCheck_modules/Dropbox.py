# Dropbox Business Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Dropbox Business (Collaboration)"

form_fields = [
    {"name": "access_token", "type": "password", "label": "Access Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Access token from Dropbox App Console. For Business, use team-scoped token."},
]


def authenticate(form_data):
    """Attempt to authenticate to Dropbox Business."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    access_token = form_data.get('access_token', '').strip()
    
    if not access_token:
        return False, "Access Token is required"
    
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Get current account
        response = requests.post("https://api.dropboxapi.com/2/users/get_current_account",
                                headers=headers, timeout=15)
        
        if response.status_code == 200:
            account = response.json()
            name = account.get('name', {}).get('display_name', 'unknown')
            email = account.get('email', 'unknown')
            account_type = account.get('account_type', {}).get('.tag', 'unknown')
            
            # Get space usage
            space_resp = requests.post("https://api.dropboxapi.com/2/users/get_space_usage",
                                      headers=headers, timeout=10)
            space_used = 0
            space_allocated = 0
            if space_resp.status_code == 200:
                space = space_resp.json()
                space_used = space.get('used', 0) / (1024**3)  # Convert to GB
                allocation = space.get('allocation', {})
                space_allocated = allocation.get('allocated', 0) / (1024**3)
            
            # Try to get team info if business account
            team_info = ""
            team_resp = requests.post("https://api.dropboxapi.com/2/team/get_info",
                                     headers=headers, timeout=10)
            if team_resp.status_code == 200:
                team = team_resp.json()
                team_name = team.get('name', 'unknown')
                team_info = f"\nTeam: {team_name}"
            
            return True, f"Successfully authenticated to Dropbox\nUser: {name} ({email})\nAccount Type: {account_type}{team_info}\nSpace: {space_used:.1f} GB / {space_allocated:.1f} GB"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Dropbox error: {e}"

