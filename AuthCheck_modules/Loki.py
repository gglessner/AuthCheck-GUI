# Grafana Loki Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Grafana Loki (Logging)"

form_fields = [
    {"name": "host", "type": "text", "label": "Loki Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "3100",
     "port_toggle": "use_ssl", "tls_port": "3100", "non_tls_port": "3100"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "org_id", "type": "text", "label": "X-Scope-OrgID (Multi-tenant)"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "HTTP: 3100, gRPC: 3101 (TLS/non-TLS same). Auth per deployment."},
]


def authenticate(form_data):
    """Attempt to authenticate to Grafana Loki."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '3100').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    org_id = form_data.get('org_id', '').strip()
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "Loki Host is required"
    
    try:
        scheme = "https" if use_ssl else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        headers = {}
        if org_id:
            headers['X-Scope-OrgID'] = org_id
        
        auth = None
        if username:
            auth = (username, password)
        
        # Check readiness
        response = requests.get(
            f"{base_url}/ready",
            headers=headers,
            auth=auth,
            timeout=15
        )
        
        if response.status_code == 200:
            # Get labels (to verify query access)
            labels_resp = requests.get(
                f"{base_url}/loki/api/v1/labels",
                headers=headers,
                auth=auth,
                timeout=10
            )
            labels = []
            if labels_resp.status_code == 200:
                labels = labels_resp.json().get('data', [])
            
            # Get build info
            build_resp = requests.get(
                f"{base_url}/loki/api/v1/status/buildinfo",
                headers=headers,
                auth=auth,
                timeout=10
            )
            version = 'unknown'
            if build_resp.status_code == 200:
                version = build_resp.json().get('version', 'unknown')
            
            return True, f"Successfully authenticated to Grafana Loki\nHost: {host}:{port}\nVersion: {version}\nLabels: {len(labels)}\nSample: {', '.join(labels[:5]) if labels else 'none'}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Loki error: {e}"

