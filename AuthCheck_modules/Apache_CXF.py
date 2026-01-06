# Apache CXF Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache CXF (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "service_path", "type": "text", "label": "Service Path", "default": "/services"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Basic Auth", "WS-Security Username Token"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8443, Non-TLS: 8080. CXF framework - check endpoint auth."},
]


def authenticate(form_data):
    """
    Attempt to connect to Apache CXF services.
    """
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    service_path = form_data.get('service_path', '/services').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "8080"
        base_url = f"{scheme}://{host}:{port_num}{service_path}"
        
        auth = None
        if auth_type == "Basic Auth" and username:
            auth = HTTPBasicAuth(username, password)
        
        # Get services listing
        response = requests.get(base_url, auth=auth, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            # Look for service listings in response
            content = response.text.lower()
            
            # Count WSDL links
            wsdl_count = content.count('?wsdl')
            wadl_count = content.count('?_wadl')
            
            services_info = []
            if wsdl_count > 0:
                services_info.append(f"SOAP Services: {wsdl_count}")
            if wadl_count > 0:
                services_info.append(f"REST Services: {wadl_count}")
            
            if services_info:
                return True, f"Successfully connected to Apache CXF at {host}:{port_num}\n" + "\n".join(services_info)
            else:
                return True, f"Successfully connected to Apache CXF at {host}:{port_num}\nServices endpoint accessible"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"CXF error: {e}"

