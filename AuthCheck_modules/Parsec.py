# Parsec Remote Desktop Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Parsec (Remote)"

form_fields = [
    {"name": "email", "type": "text", "label": "Email"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "tfa_code", "type": "text", "label": "2FA Code (if enabled)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Parsec Teams/Enterprise. Cloud-based auth"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Parsec.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    email = form_data.get('email', '').strip()
    password = form_data.get('password', '')
    tfa_code = form_data.get('tfa_code', '').strip()
    
    if not email:
        return False, "Email is required"
    if not password:
        return False, "Password is required"
    
    try:
        session = requests.Session()
        
        # Parsec API login
        login_url = "https://kessel-api.parsec.app/v1/auth"
        headers = {"Content-Type": "application/json"}
        login_data = {
            "email": email,
            "password": password,
            "grant_type": "password"
        }
        
        if tfa_code:
            login_data["tfa"] = tfa_code
        
        import json
        response = session.post(login_url, data=json.dumps(login_data), headers=headers, timeout=15)
        
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            
            if data.get("session_id"):
                # Get user info
                me_url = "https://kessel-api.parsec.app/v1/me"
                headers["Authorization"] = f"Bearer {data.get('session_id')}"
                me_resp = session.get(me_url, headers=headers, timeout=10)
                
                name = email
                team = "Personal"
                if me_resp.status_code == 200:
                    me_data = me_resp.json()
                    name = me_data.get("name", email)
                    if me_data.get("team"):
                        team = me_data.get("team", {}).get("name", "Team")
                
                return True, f"Successfully authenticated to Parsec\nUser: {name}\nTeam: {team}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            data = response.json()
            if "tfa_required" in str(data):
                return False, "Authentication failed: 2FA code required"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Parsec error: {e}"

