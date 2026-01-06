# Gravitee Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Gravitee (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "management_port", "type": "text", "label": "Management API Port", "default": "8083"},
    {"name": "gateway_port", "type": "text", "label": "Gateway Port", "default": "8082"},
    {"name": "console_port", "type": "text", "label": "Console Port", "default": "8084"},
    {"name": "protocol", "type": "combo", "label": "Protocol",
     "options": ["Management API", "Gateway", "Console"]},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Management: 8083, Gateway: 8082, Console: 8084. admin / admin"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Gravitee.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    management_port = form_data.get('management_port', '').strip()
    gateway_port = form_data.get('gateway_port', '').strip()
    console_port = form_data.get('console_port', '').strip()
    protocol = form_data.get('protocol', 'Management API')
    use_https = form_data.get('use_https', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    scheme = "https" if use_https else "http"
    
    try:
        if protocol == "Management API":
            url = f"{scheme}://{host}:{management_port}/management/organizations/DEFAULT/environments/DEFAULT/apis"
            
            auth = (username, password) if username else None
            response = requests.get(url, auth=auth, verify=verify_ssl, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else data.get('totalElements', 0)
                return True, f"Successfully authenticated to Gravitee Management API at {host}:{management_port}\nAPIs: {count}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            else:
                return False, f"Management API returned status {response.status_code}"
                
        elif protocol == "Console":
            url = f"{scheme}://{host}:{console_port}/auth/login"
            
            response = requests.post(url, json={
                "username": username,
                "password": password
            }, verify=verify_ssl, timeout=10)
            
            if response.status_code == 200:
                return True, f"Successfully authenticated to Gravitee Console at {host}:{console_port}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            else:
                return False, f"Console returned status {response.status_code}"
        else:
            url = f"{scheme}://{host}:{gateway_port}/"
            response = requests.get(url, verify=verify_ssl, timeout=10)
            
            if response.status_code < 500:
                return True, f"Successfully connected to Gravitee Gateway at {host}:{gateway_port}"
            else:
                return False, f"Gateway returned status {response.status_code}"
                
    except Exception as e:
        return False, f"Error: {e}"

