# VictoriaMetrics Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "VictoriaMetrics (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "VictoriaMetrics Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "8428",
     "port_toggle": "use_ssl", "tls_port": "8428", "non_tls_port": "8428"},
    {"name": "username", "type": "text", "label": "Username (if auth enabled)"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 8428 (TLS/non-TLS same). No auth by default. Time-series DB."},
]


def authenticate(form_data):
    """Attempt to authenticate to VictoriaMetrics."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8428').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "VictoriaMetrics Host is required"
    
    try:
        scheme = "https" if use_ssl else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        auth = None
        if username:
            auth = (username, password)
        
        # Get health
        response = requests.get(
            f"{base_url}/health",
            auth=auth,
            timeout=15
        )
        
        if response.status_code == 200:
            # Get flags/config
            flags_resp = requests.get(
                f"{base_url}/flags",
                auth=auth,
                timeout=10
            )
            version = 'unknown'
            if flags_resp.status_code == 200:
                flags_text = flags_resp.text
                if 'version' in flags_text.lower():
                    import re
                    ver_match = re.search(r'version["\s:=]+([^\s,"]+)', flags_text, re.IGNORECASE)
                    if ver_match:
                        version = ver_match.group(1)
            
            # Get metrics count
            metrics_resp = requests.get(
                f"{base_url}/api/v1/status/tsdb",
                auth=auth,
                timeout=10
            )
            series_count = 0
            if metrics_resp.status_code == 200:
                tsdb_data = metrics_resp.json()
                series_count = tsdb_data.get('data', {}).get('totalSeries', 0)
            
            return True, f"Successfully authenticated to VictoriaMetrics\nHost: {host}:{port}\nVersion: {version}\nTotal Series: {series_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"VictoriaMetrics error: {e}"

