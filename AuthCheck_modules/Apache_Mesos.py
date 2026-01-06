# Apache Mesos Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Mesos (Container)"

form_fields = [
    {"name": "host", "type": "text", "label": "Master Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "5050",
     "port_toggle": "use_https", "tls_port": "5050", "non_tls_port": "5050"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Basic Auth", "CRAM-MD5"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Master: 5050 (TLS/non-TLS same). Default: no auth."},
]


def authenticate(form_data):
    """
    Attempt to connect to Apache Mesos Master.
    """
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Master Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "5050"
        base_url = f"{scheme}://{host}:{port_num}"
        
        auth = None
        if auth_type == "Basic Auth" and username:
            auth = HTTPBasicAuth(username, password)
        
        # Get master state
        url = f"{base_url}/state"
        response = requests.get(url, auth=auth, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('version', 'unknown')
            cluster = data.get('cluster', 'unknown')
            leader = data.get('leader', 'unknown')
            agents = len(data.get('slaves', []))
            frameworks = len(data.get('frameworks', []))
            
            return True, f"Successfully connected to Apache Mesos {version}\nCluster: {cluster}\nLeader: {leader}\nAgents: {agents}, Frameworks: {frameworks}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Mesos error: {e}"

