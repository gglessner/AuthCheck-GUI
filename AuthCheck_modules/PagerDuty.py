# PagerDuty Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "PagerDuty (Monitoring)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "key_type", "type": "combo", "label": "Key Type", "options": ["General Access Token", "User Token"], "default": "General Access Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API Key from Integrations > API Access Keys. General or User tokens supported."},
]


def authenticate(form_data):
    """Attempt to authenticate to PagerDuty."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    api_key = form_data.get('api_key', '').strip()
    key_type = form_data.get('key_type', 'General Access Token')
    
    if not api_key:
        return False, "API Key is required"
    
    try:
        headers = {
            'Authorization': f'Token token={api_key}',
            'Content-Type': 'application/json'
        }
        
        # Get current user abilities (validates token)
        response = requests.get("https://api.pagerduty.com/abilities",
                               headers=headers, timeout=10)
        
        if response.status_code == 200:
            abilities = response.json().get('abilities', [])
            
            # Get user count
            users_resp = requests.get("https://api.pagerduty.com/users?total=true&limit=1",
                                     headers=headers, timeout=10)
            user_count = 0
            if users_resp.status_code == 200:
                user_count = users_resp.json().get('total', 0)
            
            # Get service count
            services_resp = requests.get("https://api.pagerduty.com/services?total=true&limit=1",
                                        headers=headers, timeout=10)
            service_count = 0
            if services_resp.status_code == 200:
                service_count = services_resp.json().get('total', 0)
            
            # Get team count
            teams_resp = requests.get("https://api.pagerduty.com/teams?total=true&limit=1",
                                     headers=headers, timeout=10)
            team_count = 0
            if teams_resp.status_code == 200:
                team_count = teams_resp.json().get('total', 0)
            
            return True, f"Successfully authenticated to PagerDuty\nKey Type: {key_type}\nAbilities: {len(abilities)}\nUsers: {user_count}\nServices: {service_count}\nTeams: {team_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API key"
        elif response.status_code == 403:
            return False, "Authentication failed: Insufficient permissions"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"PagerDuty error: {e}"

