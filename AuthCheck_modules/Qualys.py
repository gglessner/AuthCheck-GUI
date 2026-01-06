# Qualys Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Qualys (Security)"

form_fields = [
    {"name": "platform", "type": "combo", "label": "Platform URL", "options": ["https://qualysapi.qualys.com", "https://qualysapi.qg2.apps.qualys.com", "https://qualysapi.qg3.apps.qualys.com", "https://qualysapi.qg4.apps.qualys.com"], "default": "https://qualysapi.qualys.com"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API access must be enabled for user. Platform URL depends on your Qualys subscription."},
]


def authenticate(form_data):
    """Attempt to authenticate to Qualys."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    platform = form_data.get('platform', 'https://qualysapi.qualys.com')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    if not username:
        return False, "Username is required"
    if not password:
        return False, "Password is required"
    
    try:
        auth = HTTPBasicAuth(username, password)
        headers = {'X-Requested-With': 'Python'}
        
        # Get user info
        response = requests.get(f"{platform}/msp/about.php",
                               auth=auth, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Parse XML response
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            
            user_login = root.find('.//USER_LOGIN')
            user_login = user_login.text if user_login is not None else username
            
            # Get host count
            hosts_resp = requests.post(f"{platform}/api/2.0/fo/asset/host/",
                                      auth=auth, headers=headers,
                                      data={'action': 'list', 'truncation_limit': 1},
                                      timeout=10)
            host_count = 'unknown'
            if hosts_resp.status_code == 200:
                host_root = ET.fromstring(hosts_resp.text)
                warning = host_root.find('.//WARNING')
                if warning is not None:
                    count_text = warning.find('.//TEXT')
                    if count_text is not None and 'of' in count_text.text:
                        host_count = count_text.text.split('of')[1].strip().split()[0]
            
            return True, f"Successfully authenticated to Qualys\nUser: {user_login}\nHosts: {host_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Qualys error: {e}"

