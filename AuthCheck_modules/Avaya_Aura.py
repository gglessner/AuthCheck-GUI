# Avaya Aura Session Manager Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Avaya Aura (PBX)"

form_fields = [
    {"name": "host", "type": "text", "label": "Session Manager Host"},
    {"name": "port", "type": "text", "label": "HTTPS Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: admin/admin123!. SMGR web interface."},
]


def authenticate(form_data):
    """Attempt to authenticate to Avaya Aura Session Manager."""
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
        return False, "Session Manager Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        base_url = f"https://{host}:{port}"
        session = requests.Session()
        session.verify = verify_ssl
        
        # Try SMGR login page
        login_url = f"{base_url}/SMGR/login.do"
        
        # Get login page (for CSRF token if needed)
        login_page = session.get(login_url, timeout=15)
        
        # Attempt login
        login_data = {
            'userName': username,
            'password': password,
            'loginButton': 'Log On'
        }
        
        response = session.post(
            f"{base_url}/SMGR/j_security_check",
            data=login_data,
            timeout=15,
            allow_redirects=True
        )
        
        # Check if login succeeded by looking for logout link or error
        if 'logout' in response.text.lower() or 'welcome' in response.text.lower():
            return True, f"Successfully authenticated to Avaya Aura SMGR\nHost: {host}:{port}\nUser: {username}\nWeb Access: Granted"
        elif 'invalid' in response.text.lower() or 'error' in response.text.lower():
            return False, "Authentication failed: Invalid credentials"
        else:
            # Try REST API
            api_url = f"{base_url}/SMGR/services/rest/system/status"
            api_resp = session.get(api_url, auth=(username, password), timeout=10)
            
            if api_resp.status_code == 200:
                return True, f"Successfully authenticated to Avaya Aura SMGR\nHost: {host}:{port}\nREST API: Accessible"
            elif api_resp.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            else:
                return False, f"Unable to verify login - HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Avaya Aura error: {e}"

