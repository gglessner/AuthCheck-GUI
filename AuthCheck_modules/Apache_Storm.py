# Apache Storm Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Storm (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Nimbus Host", "default": "localhost"},
    {"name": "ui_port", "type": "text", "label": "UI Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Basic Auth", "Kerberos"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8443, Non-TLS: 8080. storm / storm"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Storm UI.
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
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Nimbus Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = ui_port if ui_port else "8080"
        base_url = f"{scheme}://{host}:{port_num}/api/v1"
        
        auth = None
        if auth_type == "Basic Auth" and username:
            auth = HTTPBasicAuth(username, password)
        
        # Get cluster summary
        url = f"{base_url}/cluster/summary"
        response = requests.get(url, auth=auth, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('stormVersion', 'unknown')
            supervisors = data.get('supervisors', 0)
            topologies = data.get('topologies', 0)
            slots_total = data.get('slotsTotal', 0)
            slots_used = data.get('slotsUsed', 0)
            
            return True, f"Successfully connected to Apache Storm {version}\nSupervisors: {supervisors}, Topologies: {topologies}\nSlots: {slots_used}/{slots_total}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Storm error: {e}"

