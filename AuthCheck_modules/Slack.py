# Slack Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Slack (Collaboration)"

form_fields = [
    {"name": "token", "type": "password", "label": "Bot/User Token"},
    {"name": "token_type", "type": "combo", "label": "Token Type", "options": ["Bot Token (xoxb)", "User Token (xoxp)", "App Token (xapp)"], "default": "Bot Token (xoxb)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Bot Token: xoxb-xxx. User Token: xoxp-xxx. From api.slack.com > Your Apps > OAuth & Permissions."},
]


def authenticate(form_data):
    """Attempt to authenticate to Slack."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    token = form_data.get('token', '').strip()
    token_type = form_data.get('token_type', 'Bot Token (xoxb)')
    
    if not token:
        return False, "Token is required"
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Test authentication
        response = requests.post("https://slack.com/api/auth.test",
                                headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('ok'):
                user = data.get('user', 'unknown')
                team = data.get('team', 'unknown')
                user_id = data.get('user_id', 'unknown')
                team_id = data.get('team_id', 'unknown')
                
                # Get team info
                team_resp = requests.post("https://slack.com/api/team.info",
                                         headers=headers, timeout=10)
                team_name = team
                if team_resp.status_code == 200 and team_resp.json().get('ok'):
                    team_name = team_resp.json().get('team', {}).get('name', team)
                
                # Get channel count (if has permission)
                channels_resp = requests.post("https://slack.com/api/conversations.list",
                                             headers=headers, 
                                             json={'limit': 1},
                                             timeout=10)
                channel_info = ""
                
                return True, f"Successfully authenticated to Slack\nWorkspace: {team_name}\nUser: {user}\nUser ID: {user_id}\nTeam ID: {team_id}"
            else:
                error = data.get('error', 'Unknown error')
                return False, f"Authentication failed: {error}"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Slack error: {e}"

