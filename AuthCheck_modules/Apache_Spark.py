# Apache Spark Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Spark (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Spark Master Host", "default": "localhost"},
    {"name": "ui_port", "type": "text", "label": "Web UI Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "8480", "non_tls_port": "8080"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Basic Auth", "Kerberos"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "ssl_ca", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8480, Non-TLS: 8080. Default: no auth. spark / spark"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Spark Web UI/REST API.
    """
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    ui_port = form_data.get('ui_port', '').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    ssl_ca = form_data.get('ssl_ca', '').strip()
    
    if not host:
        return False, "Spark Master Host is required"
    if not ui_port:
        return False, "Web UI Port is required"
    
    try:
        scheme = "https" if use_https else "http"
        url = f"{scheme}://{host}:{ui_port}/api/v1/applications"
        
        auth = None
        if auth_type == "Basic Auth" and username:
            auth = HTTPBasicAuth(username, password)
        
        verify = ssl_ca if ssl_ca else (not use_https)
        
        response = requests.get(url, auth=auth, timeout=10, verify=verify)
        
        if response.status_code == 200:
            apps = response.json()
            app_count = len(apps) if isinstance(apps, list) else 0
            
            # Try to get version info
            version_url = f"{scheme}://{host}:{ui_port}/api/v1/version"
            try:
                ver_response = requests.get(version_url, auth=auth, timeout=5, verify=verify)
                if ver_response.status_code == 200:
                    version = ver_response.json().get('spark', 'unknown')
                else:
                    version = 'unknown'
            except:
                version = 'unknown'
            
            return True, f"Successfully connected to Apache Spark {version}\nApplications: {app_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except requests.exceptions.SSLError as e:
        return False, f"SSL error: {e}"
    except requests.exceptions.ConnectionError as e:
        return False, f"Connection error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

