# Squid Proxy Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Squid (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Proxy Port", "default": "3128"},
    {"name": "cache_mgr_port", "type": "text", "label": "Cache Manager Port", "default": "3128"},
    {"name": "protocol", "type": "combo", "label": "Protocol",
     "options": ["HTTP Proxy", "Cache Manager"]},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Basic", "Digest", "NTLM"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "mgr_password", "type": "password", "label": "Cache Manager Password"},
    {"name": "test_url", "type": "text", "label": "Test URL", "default": "http://www.example.com"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default port: 3128. Cache manager: cache_object://hostname/info"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Squid Proxy.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    cache_mgr_port = form_data.get('cache_mgr_port', '').strip()
    protocol = form_data.get('protocol', 'HTTP Proxy')
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    mgr_password = form_data.get('mgr_password', '').strip()
    test_url = form_data.get('test_url', 'http://www.example.com').strip()
    
    if not host:
        return False, "Host is required"
    if not port:
        return False, "Port is required"
    
    try:
        if protocol == "Cache Manager":
            url = f"http://{host}:{cache_mgr_port}/squid-internal-mgr/info"
            
            headers = {}
            if mgr_password:
                import base64
                creds = base64.b64encode(f":{mgr_password}".encode()).decode()
                headers['Authorization'] = f"Basic {creds}"
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return True, f"Successfully connected to Squid Cache Manager at {host}:{cache_mgr_port}"
            elif response.status_code == 401 or response.status_code == 403:
                return False, "Cache Manager authentication failed"
            elif response.status_code == 404:
                return False, "Cache Manager not enabled or accessible"
            else:
                return False, f"Cache Manager returned status {response.status_code}"
        else:
            proxies = {
                'http': f"http://{host}:{port}",
                'https': f"http://{host}:{port}"
            }
            
            auth = None
            if auth_type == "Basic" and username:
                proxies = {
                    'http': f"http://{username}:{password}@{host}:{port}",
                    'https': f"http://{username}:{password}@{host}:{port}"
                }
            
            response = requests.get(test_url, proxies=proxies, timeout=15)
            
            via = response.headers.get('Via', '')
            x_cache = response.headers.get('X-Cache', '')
            
            if response.status_code == 407:
                return False, "Proxy authentication required"
            elif response.status_code == 403:
                return False, "Access denied by proxy"
            elif response.status_code < 400:
                if 'squid' in via.lower() or 'squid' in x_cache.lower():
                    return True, f"Successfully authenticated to Squid at {host}:{port}\nVia: {via}"
                else:
                    return True, f"Successfully connected through proxy at {host}:{port}"
            else:
                return False, f"Proxy returned status {response.status_code}"
                
    except requests.exceptions.ProxyError as e:
        if "407" in str(e):
            return False, "Proxy authentication failed"
        return False, f"Proxy error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

