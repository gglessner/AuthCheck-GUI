# Zendesk Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Zendesk (ITSM)"

form_fields = [
    {"name": "subdomain", "type": "text", "label": "Subdomain"},
    {"name": "email", "type": "text", "label": "Email"},
    {"name": "api_token", "type": "password", "label": "API Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Subdomain from URL: xxx.zendesk.com. API token from Admin > Channels > API."},
]


def authenticate(form_data):
    """Attempt to authenticate to Zendesk."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    subdomain = form_data.get('subdomain', '').strip()
    email = form_data.get('email', '').strip()
    api_token = form_data.get('api_token', '').strip()
    
    if not subdomain:
        return False, "Subdomain is required"
    if not email:
        return False, "Email is required"
    if not api_token:
        return False, "API Token is required"
    
    try:
        # Zendesk API token auth uses email/token format
        auth = HTTPBasicAuth(f"{email}/token", api_token)
        base_url = f"https://{subdomain}.zendesk.com/api/v2"
        
        # Get current user
        response = requests.get(f"{base_url}/users/me.json",
                               auth=auth, timeout=15)
        
        if response.status_code == 200:
            user = response.json().get('user', {})
            user_name = user.get('name', 'unknown')
            role = user.get('role', 'unknown')
            
            # Get ticket count
            tickets_resp = requests.get(f"{base_url}/tickets/count.json",
                                       auth=auth, timeout=10)
            ticket_count = 0
            if tickets_resp.status_code == 200:
                ticket_count = tickets_resp.json().get('count', {}).get('value', 0)
            
            # Get user count
            users_resp = requests.get(f"{base_url}/users/count.json",
                                     auth=auth, timeout=10)
            user_count = 0
            if users_resp.status_code == 200:
                user_count = users_resp.json().get('count', {}).get('value', 0)
            
            # Get organization count
            orgs_resp = requests.get(f"{base_url}/organizations/count.json",
                                    auth=auth, timeout=10)
            org_count = 0
            if orgs_resp.status_code == 200:
                org_count = orgs_resp.json().get('count', {}).get('value', 0)
            
            return True, f"Successfully authenticated to Zendesk\nSubdomain: {subdomain}\nUser: {user_name} ({role})\nTickets: {ticket_count}\nUsers: {user_count}\nOrganizations: {org_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Zendesk error: {e}"

