# Apache Tomcat Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Tomcat (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "manager_path", "type": "text", "label": "Manager Path", "default": "/manager/status"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8443, Non-TLS: 8080. tomcat / tomcat, admin / admin"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Tomcat Manager.
    """
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    manager_path = form_data.get('manager_path', '/manager/status').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "8080"
        base_url = f"{scheme}://{host}:{port_num}"
        
        auth = HTTPBasicAuth(username, password)
        
        # Try manager status
        url = f"{base_url}{manager_path}"
        response = requests.get(url, auth=auth, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            # Try to get server info
            info_url = f"{base_url}/manager/text/serverinfo"
            info_response = requests.get(info_url, auth=auth, verify=verify_ssl, timeout=10)
            
            server_info = ""
            if info_response.status_code == 200:
                lines = info_response.text.strip().split('\n')
                for line in lines:
                    if 'Tomcat Version' in line or 'Server version' in line:
                        server_info = line.strip()
                        break
            
            if server_info:
                return True, f"Successfully authenticated to Apache Tomcat at {host}:{port_num}\n{server_info}"
            else:
                return True, f"Successfully authenticated to Apache Tomcat at {host}:{port_num}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden (check user roles)"
        elif response.status_code == 404:
            return False, f"Manager app not found at {manager_path}"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Tomcat error: {e}"

