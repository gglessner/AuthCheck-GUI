# SentinelOne Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "SentinelOne (EDR)"

form_fields = [
    {"name": "console_url", "type": "text", "label": "Console URL"},
    {"name": "api_token", "type": "password", "label": "API Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API token from Settings > Users > API Token. Console URL: xxx.sentinelone.net"},
]


def authenticate(form_data):
    """Attempt to authenticate to SentinelOne."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    console_url = form_data.get('console_url', '').strip()
    api_token = form_data.get('api_token', '').strip()
    
    if not console_url:
        return False, "Console URL is required"
    if not api_token:
        return False, "API Token is required"
    
    if not console_url.startswith('http'):
        console_url = f"https://{console_url}"
    console_url = console_url.rstrip('/')
    
    try:
        headers = {
            'Authorization': f'ApiToken {api_token}',
            'Content-Type': 'application/json'
        }
        
        # Get system info
        response = requests.get(f"{console_url}/web/api/v2.1/system/info",
                               headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Get agent count
            agents_resp = requests.get(f"{console_url}/web/api/v2.1/agents/count",
                                      headers=headers, timeout=10)
            agent_count = 0
            if agents_resp.status_code == 200:
                agent_count = agents_resp.json().get('data', {}).get('total', 0)
            
            # Get threat count
            threats_resp = requests.get(f"{console_url}/web/api/v2.1/threats?resolved=false&limit=1",
                                       headers=headers, timeout=10)
            threat_count = 0
            if threats_resp.status_code == 200:
                threat_count = threats_resp.json().get('pagination', {}).get('totalItems', 0)
            
            # Get site count
            sites_resp = requests.get(f"{console_url}/web/api/v2.1/sites",
                                     headers=headers, timeout=10)
            site_count = 0
            if sites_resp.status_code == 200:
                site_count = sites_resp.json().get('pagination', {}).get('totalItems', 0)
            
            return True, f"Successfully authenticated to SentinelOne\nSites: {site_count}\nAgents: {agent_count}\nActive Threats: {threat_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"SentinelOne error: {e}"

