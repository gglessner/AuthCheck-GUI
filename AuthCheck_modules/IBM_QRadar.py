# IBM QRadar Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "IBM QRadar (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "Console Host"},
    {"name": "api_token", "type": "password", "label": "API Token"},
    {"name": "username", "type": "text", "label": "Username (Alternative)"},
    {"name": "password", "type": "password", "label": "Password (Alternative)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / (set at install). API token from Admin > Authorized Services."},
]


def authenticate(form_data):
    """Attempt to authenticate to IBM QRadar."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    api_token = form_data.get('api_token', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Console Host is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        if api_token:
            headers = {'SEC': api_token, 'Accept': 'application/json'}
        elif username and password:
            from requests.auth import HTTPBasicAuth
            session.auth = HTTPBasicAuth(username, password)
            headers = {'Accept': 'application/json'}
        else:
            return False, "API Token or Username/Password required"
        
        # Get system info
        response = session.get(f"{host}/api/system/about",
                              headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('build_version', 'unknown')
            
            # Get offense count
            offenses_resp = session.get(f"{host}/api/siem/offenses?filter=status%3DOPEN",
                                       headers=headers, timeout=10)
            offense_count = 0
            if offenses_resp.status_code == 200:
                offense_count = len(offenses_resp.json())
            
            # Get log source count
            logsources_resp = session.get(f"{host}/api/config/event_sources/log_source_management/log_sources",
                                         headers=headers, timeout=10)
            logsource_count = 0
            if logsources_resp.status_code == 200:
                logsource_count = len(logsources_resp.json())
            
            return True, f"Successfully authenticated to QRadar {version}\nOpen Offenses: {offense_count}\nLog Sources: {logsource_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"QRadar error: {e}"

