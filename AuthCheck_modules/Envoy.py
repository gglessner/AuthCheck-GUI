# Envoy Proxy Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Envoy Proxy (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "admin_port", "type": "text", "label": "Admin Port", "default": "9901",
     "port_toggle": "use_https", "tls_port": "9901", "non_tls_port": "9901"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Admin: 9901 (TLS/non-TLS same). Default: no auth. xDS: mTLS."},
]


def authenticate(form_data):
    """Attempt to connect to Envoy admin interface."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    admin_port = form_data.get('admin_port', '9901').strip()
    use_https = form_data.get('use_https', False)
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{admin_port}"
        
        # Get server info
        response = requests.get(f"{base_url}/server_info", verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('version', 'unknown')
            state = data.get('state', 'unknown')
            uptime = data.get('uptime_current_epoch', 'unknown')
            
            # Get clusters
            clusters_resp = requests.get(f"{base_url}/clusters?format=json", 
                                        verify=verify_ssl, timeout=10)
            clusters = 0
            if clusters_resp.status_code == 200:
                clusters_data = clusters_resp.json()
                clusters = len(clusters_data.get('cluster_statuses', []))
            
            return True, f"Successfully connected to Envoy {version}\nState: {state}\nClusters: {clusters}"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, f"Envoy error: {e}"

