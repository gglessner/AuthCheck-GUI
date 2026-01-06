# Heroku Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Heroku (Cloud)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API key from dashboard.heroku.com/account > API Key. Or use heroku auth:token."},
]


def authenticate(form_data):
    """Attempt to authenticate to Heroku."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    api_key = form_data.get('api_key', '').strip()
    
    if not api_key:
        return False, "API Key is required"
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/vnd.heroku+json; version=3',
            'Content-Type': 'application/json'
        }
        
        # Get account info
        response = requests.get("https://api.heroku.com/account",
                               headers=headers, timeout=15)
        
        if response.status_code == 200:
            account = response.json()
            email = account.get('email', 'unknown')
            name = account.get('name', 'unknown')
            verified = account.get('verified', False)
            
            # Get apps
            apps_resp = requests.get("https://api.heroku.com/apps",
                                    headers=headers, timeout=10)
            app_count = 0
            app_names = []
            if apps_resp.status_code == 200:
                apps = apps_resp.json()
                app_count = len(apps)
                app_names = [a['name'] for a in apps[:3]]
            
            # Get teams
            teams_resp = requests.get("https://api.heroku.com/teams",
                                     headers=headers, timeout=10)
            team_count = 0
            if teams_resp.status_code == 200:
                team_count = len(teams_resp.json())
            
            verified_str = "Yes" if verified else "No"
            return True, f"Successfully authenticated to Heroku\nUser: {name} ({email})\nVerified: {verified_str}\nApps: {app_count}\nTeams: {team_count}\nSample Apps: {', '.join(app_names) if app_names else 'none'}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API key"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Heroku error: {e}"

