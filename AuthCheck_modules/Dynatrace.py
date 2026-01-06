# Dynatrace Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Dynatrace (Monitoring)"

form_fields = [
    {"name": "environment_url", "type": "text", "label": "Environment URL"},
    {"name": "api_token", "type": "password", "label": "API Token"},
    {"name": "env_type", "type": "combo", "label": "Environment Type", "options": ["SaaS", "Managed"], "default": "SaaS"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "SaaS URL: xxx.live.dynatrace.com. Managed: your-domain/e/env-id. API token from Settings > Integration > Dynatrace API."},
]


def authenticate(form_data):
    """Attempt to authenticate to Dynatrace."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    environment_url = form_data.get('environment_url', '').strip()
    api_token = form_data.get('api_token', '').strip()
    env_type = form_data.get('env_type', 'SaaS')
    
    if not environment_url:
        return False, "Environment URL is required"
    if not api_token:
        return False, "API Token is required"
    
    # Normalize URL
    if not environment_url.startswith('http'):
        environment_url = f"https://{environment_url}"
    environment_url = environment_url.rstrip('/')
    
    try:
        headers = {
            'Authorization': f'Api-Token {api_token}',
            'Content-Type': 'application/json'
        }
        
        # Get cluster version
        response = requests.get(f"{environment_url}/api/v1/config/clusterversion",
                               headers=headers, timeout=10)
        
        if response.status_code == 200:
            version = response.json().get('version', 'unknown')
            
            # Get environment info
            env_resp = requests.get(f"{environment_url}/api/v2/entities",
                                   headers=headers, timeout=10,
                                   params={'entitySelector': 'type("HOST")', 'pageSize': 1})
            host_count = 0
            if env_resp.status_code == 200:
                host_count = env_resp.json().get('totalCount', 0)
            
            # Get token permissions
            token_resp = requests.get(f"{environment_url}/api/v2/apiTokens/current",
                                     headers=headers, timeout=10)
            token_name = 'unknown'
            scopes = []
            if token_resp.status_code == 200:
                token_data = token_resp.json()
                token_name = token_data.get('name', 'unknown')
                scopes = token_data.get('scopes', [])
            
            return True, f"Successfully authenticated to Dynatrace {version}\nToken: {token_name}\nHosts monitored: {host_count}\nScopes: {len(scopes)}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API token"
        elif response.status_code == 403:
            return False, "Authentication failed: Insufficient permissions"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Dynatrace error: {e}"

