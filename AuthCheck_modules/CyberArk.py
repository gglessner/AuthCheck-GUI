# CyberArk Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "CyberArk PAS (IAM)"

form_fields = [
    {"name": "pvwa_url", "type": "text", "label": "PVWA URL"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["CyberArk", "LDAP", "RADIUS", "Windows"], "default": "CyberArk"},
    {"name": "new_password", "type": "password", "label": "New Password (if required)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "PVWA URL: https://pvwa.domain.com/PasswordVault. Administrator / (set during install)."},
]


def authenticate(form_data):
    """Attempt to authenticate to CyberArk PAS."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    pvwa_url = form_data.get('pvwa_url', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    auth_type = form_data.get('auth_type', 'CyberArk')
    new_password = form_data.get('new_password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not pvwa_url:
        return False, "PVWA URL is required"
    if not username:
        return False, "Username is required"
    
    # Normalize URL
    if not pvwa_url.startswith('http'):
        pvwa_url = f"https://{pvwa_url}"
    pvwa_url = pvwa_url.rstrip('/')
    
    try:
        # Map auth type to API path
        auth_paths = {
            'CyberArk': 'CyberArk',
            'LDAP': 'LDAP',
            'RADIUS': 'RADIUS',
            'Windows': 'Windows'
        }
        auth_path = auth_paths.get(auth_type, 'CyberArk')
        
        headers = {'Content-Type': 'application/json'}
        
        login_data = {
            'username': username,
            'password': password
        }
        
        if new_password:
            login_data['newPassword'] = new_password
        
        response = requests.post(f"{pvwa_url}/API/Auth/{auth_path}/Logon",
                                json=login_data, headers=headers,
                                verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            token = response.text.strip('"')
            
            # Get user details
            auth_headers = {
                'Authorization': token,
                'Content-Type': 'application/json'
            }
            
            # Get safes count
            safes_resp = requests.get(f"{pvwa_url}/API/Safes",
                                     headers=auth_headers, verify=verify_ssl, timeout=10)
            safe_count = 0
            if safes_resp.status_code == 200:
                safes_data = safes_resp.json()
                safe_count = safes_data.get('Total', len(safes_data.get('Safes', [])))
            
            # Logoff
            requests.post(f"{pvwa_url}/API/Auth/Logoff",
                         headers=auth_headers, verify=verify_ssl, timeout=5)
            
            return True, f"Successfully authenticated to CyberArk PAS\nUser: {username}\nAuth Type: {auth_type}\nAccessible Safes: {safe_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Authentication failed: User suspended or requires password change"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"CyberArk error: {e}"

