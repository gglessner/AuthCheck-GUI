# pfSense Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "pfSense (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "pfSense Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password", "default": "pfsense"},
    {"name": "api_key", "type": "password", "label": "API Key (pfSense-API)"},
    {"name": "api_secret", "type": "password", "label": "API Secret (pfSense-API)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: admin/pfsense. API requires pfSense-API package installed."},
]


def authenticate(form_data):
    """Attempt to authenticate to pfSense."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    api_key = form_data.get('api_key', '').strip()
    api_secret = form_data.get('api_secret', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "pfSense Host is required"
    
    try:
        base_url = f"https://{host}:{port}"
        session = requests.Session()
        session.verify = verify_ssl
        
        if api_key and api_secret:
            # Use pfSense-API
            headers = {
                'Authorization': f'{api_key} {api_secret}',
                'Content-Type': 'application/json'
            }
            
            response = session.get(
                f"{base_url}/api/v1/system/version",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                version = data.get('version', 'unknown')
                
                return True, f"Successfully authenticated to pfSense (API)\nHost: {host}\nVersion: {version}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid API credentials"
        else:
            # Web UI login
            if not username:
                return False, "Username or API Key required"
            
            # Get CSRF token
            login_page = session.get(f"{base_url}/", timeout=10)
            
            # Extract CSRF token
            import re
            csrf_match = re.search(r"name=['\"]__csrf_magic['\"] value=['\"]([^'\"]+)['\"]", login_page.text)
            csrf_token = csrf_match.group(1) if csrf_match else ''
            
            # Login
            login_resp = session.post(
                f"{base_url}/index.php",
                data={
                    '__csrf_magic': csrf_token,
                    'usernamefld': username,
                    'passwordfld': password,
                    'login': 'Sign In'
                },
                timeout=15
            )
            
            if 'Dashboard' in login_resp.text or 'logout.php' in login_resp.text:
                # Extract version if visible
                version_match = re.search(r'Version.*?(\d+\.\d+(?:\.\d+)?)', login_resp.text)
                version = version_match.group(1) if version_match else 'unknown'
                
                return True, f"Successfully authenticated to pfSense (Web UI)\nHost: {host}\nUser: {username}\nVersion: {version}"
            else:
                return False, "Authentication failed: Invalid credentials"
                
    except Exception as e:
        return False, f"pfSense error: {e}"

