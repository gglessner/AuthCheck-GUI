# Checkmk Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Checkmk (Monitoring)"

form_fields = [
    {"name": "url", "type": "text", "label": "Checkmk URL"},
    {"name": "site", "type": "text", "label": "Site Name"},
    {"name": "username", "type": "text", "label": "Username", "default": "cmkadmin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: cmkadmin/(generated). Site name from URL path."},
]


def authenticate(form_data):
    """Attempt to authenticate to Checkmk."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', '').strip()
    site = form_data.get('site', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not url:
        return False, "Checkmk URL is required"
    if not site:
        return False, "Site Name is required"
    if not username:
        return False, "Username is required"
    
    if not url.startswith('http'):
        url = f"https://{url}"
    url = url.rstrip('/')
    
    try:
        # REST API authentication
        api_url = f"{url}/{site}/check_mk/api/1.0"
        headers = {
            'Authorization': f'Bearer {username} {password}',
            'Accept': 'application/json'
        }
        
        response = requests.get(
            f"{api_url}/version",
            headers=headers,
            verify=verify_ssl,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('versions', {}).get('checkmk', 'unknown')
            edition = data.get('edition', 'unknown')
            
            # Get hosts count
            hosts_resp = requests.get(
                f"{api_url}/domain-types/host_config/collections/all",
                headers=headers,
                verify=verify_ssl,
                timeout=10
            )
            host_count = 0
            if hosts_resp.status_code == 200:
                host_count = len(hosts_resp.json().get('value', []))
            
            return True, f"Successfully authenticated to Checkmk\nSite: {site}\nVersion: {version}\nEdition: {edition}\nHosts: {host_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Checkmk error: {e}"

