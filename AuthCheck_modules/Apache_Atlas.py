# Apache Atlas Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Atlas (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Atlas Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "21000",
     "port_toggle": "use_https", "tls_port": "21443", "non_tls_port": "21000"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 21443, Non-TLS: 21000. admin / admin"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Atlas.
    """
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Atlas Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "21000"
        base_url = f"{scheme}://{host}:{port_num}/api/atlas"
        
        auth = HTTPBasicAuth(username, password)
        
        # Get admin status
        url = f"{base_url}/admin/status"
        response = requests.get(url, auth=auth, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('Status', 'unknown')
            
            # Get version
            ver_url = f"{base_url}/admin/version"
            ver_response = requests.get(ver_url, auth=auth, verify=verify_ssl, timeout=10)
            version = 'unknown'
            if ver_response.status_code == 200:
                version = ver_response.json().get('Version', 'unknown')
            
            # Get types count
            types_url = f"{base_url}/v2/types/typedefs"
            types_response = requests.get(types_url, auth=auth, verify=verify_ssl, timeout=10)
            type_count = 0
            if types_response.status_code == 200:
                types_data = types_response.json()
                type_count = len(types_data.get('entityDefs', []))
            
            return True, f"Successfully authenticated to Apache Atlas {version}\nStatus: {status}, Entity Types: {type_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Atlas error: {e}"

