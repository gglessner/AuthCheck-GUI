# Spring Cloud Gateway Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Spring Cloud Gateway (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "actuator_port", "type": "text", "label": "Actuator Port", "default": "8081"},
    {"name": "protocol", "type": "combo", "label": "Protocol",
     "options": ["Gateway", "Actuator"]},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Basic", "Bearer Token"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password/Token"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Gateway: 8080, Actuator: 8081. Actuator endpoint: /actuator/gateway/routes"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Spring Cloud Gateway.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    actuator_port = form_data.get('actuator_port', '').strip()
    protocol = form_data.get('protocol', 'Gateway')
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    scheme = "https" if use_https else "http"
    
    try:
        headers = {}
        auth = None
        
        if auth_type == "Basic" and username:
            auth = (username, password)
        elif auth_type == "Bearer Token" and password:
            headers['Authorization'] = f"Bearer {password}"
        
        if protocol == "Actuator":
            url = f"{scheme}://{host}:{actuator_port}/actuator/gateway/routes"
            
            response = requests.get(url, auth=auth, headers=headers, verify=verify_ssl, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                return True, f"Successfully connected to Spring Cloud Gateway Actuator at {host}:{actuator_port}\nRoutes: {count}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            elif response.status_code == 404:
                # Try health endpoint
                url = f"{scheme}://{host}:{actuator_port}/actuator/health"
                response = requests.get(url, auth=auth, headers=headers, verify=verify_ssl, timeout=10)
                if response.status_code == 200:
                    return True, f"Successfully connected to Actuator at {host}:{actuator_port} (gateway routes not exposed)"
                return False, "Actuator endpoints not found"
            else:
                return False, f"Actuator returned status {response.status_code}"
        else:
            url = f"{scheme}://{host}:{port}/"
            
            response = requests.get(url, auth=auth, headers=headers, verify=verify_ssl, timeout=10)
            
            if response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            elif response.status_code < 500:
                return True, f"Successfully connected to Spring Cloud Gateway at {host}:{port}"
            else:
                return False, f"Gateway returned status {response.status_code}"
                
    except Exception as e:
        return False, f"Error: {e}"

