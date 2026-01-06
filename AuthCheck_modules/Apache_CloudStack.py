# Apache CloudStack Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache CloudStack (Cloud)"

form_fields = [
    {"name": "host", "type": "text", "label": "Management Server", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "api_path", "type": "text", "label": "API Path", "default": "/client/api"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "domain", "type": "text", "label": "Domain", "default": "/"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8443, Non-TLS: 8080. admin / password"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache CloudStack.
    """
    try:
        import requests
        import hashlib
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    api_path = form_data.get('api_path', '/client/api').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    domain = form_data.get('domain', '/').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Management Server is required"
    if not username:
        return False, "Username is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "8080"
        base_url = f"{scheme}://{host}:{port_num}{api_path}"
        
        session = requests.Session()
        
        # Login command
        params = {
            "command": "login",
            "username": username,
            "password": hashlib.md5(password.encode()).hexdigest(),
            "domain": domain,
            "response": "json"
        }
        
        response = session.post(base_url, data=params, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'loginresponse' in data:
                login_data = data['loginresponse']
                user = login_data.get('username', username)
                account = login_data.get('account', 'unknown')
                account_type = login_data.get('type', 'unknown')
                
                # Get zones
                zone_params = {"command": "listZones", "response": "json"}
                zone_response = session.get(base_url, params=zone_params, verify=verify_ssl, timeout=10)
                zones = 0
                if zone_response.status_code == 200:
                    zone_data = zone_response.json()
                    zones = zone_data.get('listzonesresponse', {}).get('count', 0)
                
                return True, f"Successfully authenticated to Apache CloudStack\nUser: {user}\nAccount: {account} (type {account_type})\nZones: {zones}"
            elif 'errorresponse' in data:
                error = data['errorresponse'].get('errortext', 'Unknown error')
                return False, f"Authentication failed: {error}"
        
        return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"CloudStack error: {e}"

