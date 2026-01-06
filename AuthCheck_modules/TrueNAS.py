# TrueNAS Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "TrueNAS / FreeNAS (NAS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.100"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "api_key", "type": "password", "label": "API Key (alternative)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "root / (set during install). HTTPS: 443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to TrueNAS/FreeNAS.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
    use_https = form_data.get('use_https', True)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    api_key = form_data.get('api_key', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    scheme = "https" if use_https else "http"
    base_url = f"{scheme}://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        headers = {}
        auth = None
        
        if api_key:
            headers['Authorization'] = f"Bearer {api_key}"
        else:
            auth = (username, password)
        
        # TrueNAS SCALE / CORE API v2
        api_url = f"{base_url}/api/v2.0/system/info"
        response = session.get(api_url, auth=auth, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            version = data.get('version', 'unknown')
            hostname = data.get('hostname', host)
            
            # Get pool info
            pool_url = f"{base_url}/api/v2.0/pool"
            pool_resp = session.get(pool_url, auth=auth, headers=headers, timeout=10)
            
            pool_count = 0
            if pool_resp.status_code == 200:
                pool_count = len(pool_resp.json())
            
            return True, f"Successfully authenticated to TrueNAS at {hostname}\nVersion: {version}\nPools: {pool_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        # Try legacy FreeNAS API v1
        api_url = f"{base_url}/api/v1.0/system/info/"
        response = session.get(api_url, auth=auth, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('version', 'unknown')
            return True, f"Successfully authenticated to FreeNAS\nVersion: {version}"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"TrueNAS error: {e}"

