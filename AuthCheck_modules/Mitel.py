# Mitel MiVoice Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Mitel MiVoice (PBX)"

form_fields = [
    {"name": "host", "type": "text", "label": "Mitel Host"},
    {"name": "port", "type": "text", "label": "HTTPS Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: admin/22222. MiVoice Business/Connect web interface."},
]


def authenticate(form_data):
    """Attempt to authenticate to Mitel MiVoice."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Mitel Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        base_url = f"https://{host}:{port}"
        session = requests.Session()
        session.verify = verify_ssl
        
        # Try MiVoice Business/Connect web login
        login_url = f"{base_url}/login"
        
        # Get login page for any tokens
        login_page = session.get(login_url, timeout=15)
        
        # Attempt login
        login_data = {
            'username': username,
            'password': password
        }
        
        response = session.post(
            login_url,
            data=login_data,
            timeout=15,
            allow_redirects=True
        )
        
        if response.status_code == 200:
            if 'logout' in response.text.lower() or 'dashboard' in response.text.lower():
                return True, f"Successfully authenticated to Mitel MiVoice\nHost: {host}:{port}\nUser: {username}\nWeb Access: Granted"
            elif 'invalid' in response.text.lower() or 'error' in response.text.lower():
                return False, "Authentication failed: Invalid credentials"
        
        # Try API authentication
        api_url = f"{base_url}/api/v1/authenticate"
        api_resp = session.post(
            api_url,
            json={'username': username, 'password': password},
            timeout=10
        )
        
        if api_resp.status_code == 200:
            return True, f"Successfully authenticated to Mitel MiVoice\nHost: {host}:{port}\nAPI Access: Granted"
        elif api_resp.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"Unable to authenticate - HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Mitel error: {e}"

