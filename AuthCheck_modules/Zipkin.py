# Zipkin Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Zipkin (Monitoring)"

form_fields = [
    {"name": "host", "type": "text", "label": "Zipkin Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "9411",
     "port_toggle": "use_ssl", "tls_port": "9411", "non_tls_port": "9411"},
    {"name": "username", "type": "text", "label": "Username (if proxy auth)"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 9411 (TLS/non-TLS same). No built-in auth; use reverse proxy."},
]


def authenticate(form_data):
    """Attempt to authenticate to Zipkin."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '9411').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "Zipkin Host is required"
    
    try:
        scheme = "https" if use_ssl else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        auth = None
        if username:
            auth = (username, password)
        
        # Get services
        response = requests.get(
            f"{base_url}/api/v2/services",
            auth=auth,
            timeout=15
        )
        
        if response.status_code == 200:
            services = response.json()
            service_count = len(services)
            
            # Get recent traces count
            traces_resp = requests.get(
                f"{base_url}/api/v2/traces?limit=100",
                auth=auth,
                timeout=10
            )
            trace_count = 0
            if traces_resp.status_code == 200:
                trace_count = len(traces_resp.json())
            
            return True, f"Successfully connected to Zipkin\nHost: {host}:{port}\nServices: {service_count}\nRecent Traces: {trace_count}\nSample: {', '.join(services[:5]) if services else 'none'}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Zipkin error: {e}"

