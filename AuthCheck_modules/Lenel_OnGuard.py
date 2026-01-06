# Lenel OnGuard Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Lenel OnGuard (Access Control)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.100"},
    {"name": "port", "type": "text", "label": "Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username", "default": "sa"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "directory", "type": "text", "label": "Directory", "default": "OnGuard"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "sa / OnGuard2015 (default). Web: 8080/8443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Lenel OnGuard.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8080').strip()
    use_https = form_data.get('use_https', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    directory = form_data.get('directory', 'OnGuard').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    scheme = "https" if use_https else "http"
    base_url = f"{scheme}://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # OnGuard API login
        login_url = f"{base_url}/api/access/onguard/openaccess/authentication"
        login_data = {
            "user_name": username,
            "password": password,
            "directory_id": directory
        }
        
        headers = {"Content-Type": "application/json"}
        import json
        
        response = session.post(login_url, data=json.dumps(login_data), headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("session_token"):
                token = data.get("session_token")
                
                # Get system info
                info_url = f"{base_url}/api/access/onguard/openaccess/system_version"
                headers["Session-Token"] = token
                info_resp = session.get(info_url, headers=headers, timeout=10)
                
                version = "unknown"
                if info_resp.status_code == 200:
                    version = info_resp.json().get("version", "unknown")
                
                return True, f"Successfully authenticated to OnGuard at {host}\nVersion: {version}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"OnGuard error: {e}"
