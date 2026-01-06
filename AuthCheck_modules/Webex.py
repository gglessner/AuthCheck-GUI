# Cisco Webex Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Cisco Webex (Collaboration)"

form_fields = [
    {"name": "access_token", "type": "password", "label": "Access Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Bot or Personal access token from developer.webex.com. Bot tokens start with Y2lz..."},
]


def authenticate(form_data):
    """Attempt to authenticate to Cisco Webex."""
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
        
        # Get current user/bot
        response = requests.get("https://webexapis.com/v1/people/me",
                               headers=headers, timeout=15)
        
        if response.status_code == 200:
            person = response.json()
            display_name = person.get('displayName', 'unknown')
            emails = person.get('emails', ['unknown'])
            person_type = person.get('type', 'unknown')
            org_id = person.get('orgId', 'unknown')[:20] + '...'
            
            # Get rooms/spaces
            rooms_resp = requests.get("https://webexapis.com/v1/rooms?max=100",
                                     headers=headers, timeout=10)
            room_count = 0
            if rooms_resp.status_code == 200:
                room_count = len(rooms_resp.json().get('items', []))
            
            # Get teams
            teams_resp = requests.get("https://webexapis.com/v1/teams",
                                     headers=headers, timeout=10)
            team_count = 0
            if teams_resp.status_code == 200:
                team_count = len(teams_resp.json().get('items', []))
            
            return True, f"Successfully authenticated to Webex\nName: {display_name}\nEmail: {emails[0]}\nType: {person_type}\nSpaces: {room_count}\nTeams: {team_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Webex error: {e}"

