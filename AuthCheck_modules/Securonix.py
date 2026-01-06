# Securonix Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Securonix (Security)"

form_fields = [
    {"name": "url", "type": "text", "label": "Securonix URL"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Credentials configured during deployment. SNYPR platform."},
]


def authenticate(form_data):
    """Attempt to authenticate to Securonix."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not url:
        return False, "Securonix URL is required"
    if not username:
        return False, "Username is required"
    
    if not url.startswith('http'):
        url = f"https://{url}"
    url = url.rstrip('/')
    
    try:
        # Get authentication token
        response = requests.get(
            f"{url}/Snypr/ws/token/generate",
            params={'username': username, 'password': password},
            verify=verify_ssl,
            timeout=15
        )
        
        if response.status_code == 200:
            token = response.text.strip()
            if token and len(token) > 20:
                headers = {'token': token}
                
                # Validate token
                validate_resp = requests.get(
                    f"{url}/Snypr/ws/token/validate",
                    headers=headers,
                    verify=verify_ssl,
                    timeout=10
                )
                
                if validate_resp.status_code == 200:
                    return True, f"Successfully authenticated to Securonix\nURL: {url}\nUser: {username}\nToken obtained and validated"
                
                return True, f"Successfully authenticated to Securonix\nURL: {url}\nUser: {username}\nToken: {token[:20]}..."
            else:
                return False, "Authentication failed: Invalid token response"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Securonix error: {e}"

