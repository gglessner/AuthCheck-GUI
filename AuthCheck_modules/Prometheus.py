# Prometheus Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Prometheus (Monitoring)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "9090",
     "port_toggle": "use_https", "tls_port": "9090", "non_tls_port": "9090"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Basic Auth", "Bearer Token"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password/Token"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 9090 (TLS/non-TLS same). Default: no auth. admin / admin"},
]


def authenticate(form_data):
    """Attempt to authenticate to Prometheus."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '9090').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{port}/api/v1"
        
        auth = None
        headers = {}
        
        if auth_type == "Basic Auth" and username:
            auth = HTTPBasicAuth(username, password)
        elif auth_type == "Bearer Token" and password:
            headers['Authorization'] = f"Bearer {password}"
        
        # Get build info
        response = requests.get(f"{base_url}/status/buildinfo", auth=auth, 
                               headers=headers, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                build = data.get('data', {})
                version = build.get('version', 'unknown')
                
                # Get targets
                targets_resp = requests.get(f"{base_url}/targets", auth=auth,
                                           headers=headers, verify=verify_ssl, timeout=10)
                active_targets = 0
                if targets_resp.status_code == 200:
                    targets_data = targets_resp.json()
                    active_targets = len(targets_data.get('data', {}).get('activeTargets', []))
                
                # Get rules count
                rules_resp = requests.get(f"{base_url}/rules", auth=auth,
                                         headers=headers, verify=verify_ssl, timeout=10)
                rules = 0
                if rules_resp.status_code == 200:
                    rules_data = rules_resp.json()
                    rules = len(rules_data.get('data', {}).get('groups', []))
                
                return True, f"Successfully connected to Prometheus {version}\nTargets: {active_targets}, Rule Groups: {rules}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, f"Prometheus error: {e}"

