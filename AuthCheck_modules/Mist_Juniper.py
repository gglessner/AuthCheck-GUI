# Mist (Juniper) Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Mist / Juniper (Wireless)"

form_fields = [
    {"name": "host", "type": "text", "label": "API Host", "default": "api.mist.com"},
    {"name": "api_token", "type": "password", "label": "API Token"},
    {"name": "username", "type": "text", "label": "Username (alternative)"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "org_id", "type": "text", "label": "Organization ID"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Cloud-based. API token from Mist Dashboard > Organization > Settings"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Mist (Juniper) Cloud.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', 'api.mist.com').strip()
    api_token = form_data.get('api_token', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    org_id = form_data.get('org_id', '').strip()
    verify_ssl = form_data.get('verify_ssl', True)
    
    if not host:
        return False, "API Host is required"
    
    base_url = f"https://{host}/api/v1"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        headers = {}
        
        if api_token:
            headers['Authorization'] = f"Token {api_token}"
        elif username and password:
            # Login with credentials
            login_url = f"{base_url}/login"
            login_data = {
                "email": username,
                "password": password
            }
            
            response = session.post(login_url, json=login_data, timeout=15)
            
            if response.status_code != 200:
                return False, "Authentication failed: Invalid credentials"
        else:
            return False, "API Token or Username/Password required"
        
        # Get self info
        self_url = f"{base_url}/self"
        response = session.get(self_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            name = user_info.get('name', user_info.get('email', 'unknown'))
            
            # Get org info if org_id provided
            if org_id:
                org_url = f"{base_url}/orgs/{org_id}/stats"
                org_resp = session.get(org_url, headers=headers, timeout=10)
                
                if org_resp.status_code == 200:
                    org_stats = org_resp.json()
                    ap_count = org_stats.get('num_devices', {}).get('ap', 0)
                    return True, f"Successfully authenticated to Mist Cloud\nUser: {name}\nAPs: {ap_count}"
            
            # Get orgs list
            orgs_url = f"{base_url}/self/orgs"
            orgs_resp = session.get(orgs_url, headers=headers, timeout=10)
            
            org_count = 0
            if orgs_resp.status_code == 200:
                org_count = len(orgs_resp.json())
            
            return True, f"Successfully authenticated to Mist Cloud\nUser: {name}\nOrganizations: {org_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API token"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Mist error: {e}"

