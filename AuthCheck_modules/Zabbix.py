# Zabbix Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Zabbix (Monitoring)"

form_fields = [
    {"name": "url", "type": "text", "label": "Zabbix URL"},
    {"name": "username", "type": "text", "label": "Username", "default": "Admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "api_token", "type": "password", "label": "API Token (Alternative)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Admin / zabbix (default). API at /api_jsonrpc.php."},
]


def authenticate(form_data):
    """Attempt to authenticate to Zabbix."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    api_token = form_data.get('api_token', '').strip()
    
    if not url:
        return False, "Zabbix URL is required"
    
    if not url.startswith('http'):
        url = f"http://{url}"
    url = url.rstrip('/')
    
    api_url = f"{url}/api_jsonrpc.php"
    
    try:
        headers = {'Content-Type': 'application/json-rpc'}
        
        if api_token:
            # Use API token (Zabbix 5.4+)
            headers['Authorization'] = f'Bearer {api_token}'
            auth_token = api_token
        else:
            if not username:
                return False, "Username or API Token is required"
            
            # Login with username/password
            login_data = {
                'jsonrpc': '2.0',
                'method': 'user.login',
                'params': {
                    'user': username,
                    'password': password
                },
                'id': 1
            }
            
            response = requests.post(api_url, json=login_data, headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if 'error' in result:
                    return False, f"Authentication failed: {result['error'].get('data', result['error'].get('message', 'Unknown'))}"
                auth_token = result.get('result')
            else:
                return False, f"HTTP {response.status_code}"
        
        # Get API version
        version_data = {
            'jsonrpc': '2.0',
            'method': 'apiinfo.version',
            'params': [],
            'id': 2
        }
        if not api_token:
            version_data['auth'] = auth_token
        
        ver_resp = requests.post(api_url, json=version_data, headers=headers, timeout=10)
        version = 'unknown'
        if ver_resp.status_code == 200:
            version = ver_resp.json().get('result', 'unknown')
        
        # Get host count
        host_data = {
            'jsonrpc': '2.0',
            'method': 'host.get',
            'params': {'countOutput': True},
            'id': 3
        }
        if not api_token:
            host_data['auth'] = auth_token
        
        host_resp = requests.post(api_url, json=host_data, headers=headers, timeout=10)
        host_count = 0
        if host_resp.status_code == 200:
            host_count = host_resp.json().get('result', 0)
        
        return True, f"Successfully authenticated to Zabbix {version}\nHosts: {host_count}"
        
    except Exception as e:
        return False, f"Zabbix error: {e}"

