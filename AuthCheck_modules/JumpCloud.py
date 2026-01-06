# JumpCloud Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "JumpCloud (IAM)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "org_id", "type": "text", "label": "Organization ID (MTP)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API Key from Admin Console > API Settings. MTP orgs need Org ID."},
]


def authenticate(form_data):
    """Attempt to authenticate to JumpCloud."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    api_key = form_data.get('api_key', '').strip()
    org_id = form_data.get('org_id', '').strip()
    
    if not api_key:
        return False, "API Key is required"
    
    try:
        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        if org_id:
            headers['x-org-id'] = org_id
        
        # Get organization info
        response = requests.get("https://console.jumpcloud.com/api/organizations",
                               headers=headers, timeout=15)
        
        if response.status_code == 200:
            orgs = response.json()
            org_name = 'unknown'
            if orgs and len(orgs) > 0:
                org_name = orgs[0].get('displayName', 'unknown')
            
            # Get user count
            users_resp = requests.get("https://console.jumpcloud.com/api/systemusers",
                                     headers=headers, timeout=10)
            user_count = 0
            if users_resp.status_code == 200:
                user_count = users_resp.json().get('totalCount', len(users_resp.json().get('results', [])))
            
            # Get system count
            systems_resp = requests.get("https://console.jumpcloud.com/api/systems",
                                       headers=headers, timeout=10)
            system_count = 0
            if systems_resp.status_code == 200:
                system_count = systems_resp.json().get('totalCount', len(systems_resp.json().get('results', [])))
            
            # Get group count
            groups_resp = requests.get("https://console.jumpcloud.com/api/v2/usergroups",
                                      headers=headers, timeout=10)
            group_count = 0
            if groups_resp.status_code == 200:
                group_count = len(groups_resp.json())
            
            return True, f"Successfully authenticated to JumpCloud\nOrganization: {org_name}\nUsers: {user_count}\nSystems: {system_count}\nUser Groups: {group_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API key"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"JumpCloud error: {e}"

