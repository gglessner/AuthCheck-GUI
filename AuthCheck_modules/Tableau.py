# Tableau Server Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Tableau Server (Analytics)"

form_fields = [
    {"name": "server_url", "type": "text", "label": "Server URL"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "site_id", "type": "text", "label": "Site ID", "default": ""},
    {"name": "token_name", "type": "text", "label": "Personal Access Token Name"},
    {"name": "token_secret", "type": "password", "label": "Personal Access Token Secret"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Site ID blank for default site. PAT from My Account Settings > Personal Access Tokens."},
]


def authenticate(form_data):
    """Attempt to authenticate to Tableau Server."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    server_url = form_data.get('server_url', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    site_id = form_data.get('site_id', '').strip()
    token_name = form_data.get('token_name', '').strip()
    token_secret = form_data.get('token_secret', '')
    
    if not server_url:
        return False, "Server URL is required"
    
    if not server_url.startswith('http'):
        server_url = f"https://{server_url}"
    server_url = server_url.rstrip('/')
    
    try:
        api_url = f"{server_url}/api/3.19"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if token_name and token_secret:
            # Personal Access Token authentication
            signin_data = {
                'credentials': {
                    'personalAccessTokenName': token_name,
                    'personalAccessTokenSecret': token_secret,
                    'site': {'contentUrl': site_id}
                }
            }
        else:
            if not username:
                return False, "Username or Personal Access Token required"
            # Username/password authentication
            signin_data = {
                'credentials': {
                    'name': username,
                    'password': password,
                    'site': {'contentUrl': site_id}
                }
            }
        
        response = requests.post(f"{api_url}/auth/signin",
                                json=signin_data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            credentials = data.get('credentials', {})
            token = credentials.get('token')
            site = credentials.get('site', {})
            user = credentials.get('user', {})
            
            site_name = site.get('name', 'Default')
            user_name = user.get('name', username)
            
            # Get server info
            headers['X-Tableau-Auth'] = token
            
            # Get workbook count
            workbooks_resp = requests.get(f"{api_url}/sites/{site.get('id')}/workbooks",
                                         headers=headers, timeout=10)
            workbook_count = 0
            if workbooks_resp.status_code == 200:
                workbook_count = workbooks_resp.json().get('pagination', {}).get('totalAvailable', 0)
            
            # Sign out
            requests.post(f"{api_url}/auth/signout", headers=headers, timeout=5)
            
            return True, f"Successfully authenticated to Tableau Server\nSite: {site_name}\nUser: {user_name}\nWorkbooks: {workbook_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('detail', response.text[:200])
            except:
                error_msg = response.text[:200]
            return False, f"Authentication failed: {error_msg}"
            
    except Exception as e:
        return False, f"Tableau error: {e}"

