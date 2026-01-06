# Apache Oozie Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Oozie (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Oozie Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "11000",
     "port_toggle": "use_https", "tls_port": "11443", "non_tls_port": "11000"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Kerberos", "Simple"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 11443, Non-TLS: 11000. oozie / oozie"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Oozie.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Oozie Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "11000"
        base_url = f"{scheme}://{host}:{port_num}/oozie"
        
        params = {}
        if auth_type == "Simple" and username:
            params['user.name'] = username
        
        # Get Oozie status
        url = f"{base_url}/v1/admin/status"
        response = requests.get(url, params=params, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('systemMode', 'unknown')
            
            # Get build version
            ver_url = f"{base_url}/v1/admin/build-version"
            ver_response = requests.get(ver_url, params=params, verify=verify_ssl, timeout=10)
            version = 'unknown'
            if ver_response.status_code == 200:
                version = ver_response.json().get('buildVersion', 'unknown')
            
            return True, f"Successfully connected to Apache Oozie {version}\nSystem Mode: {status}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Oozie error: {e}"

