# Apache Traffic Server Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Traffic Server (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "stats_port", "type": "text", "label": "Stats Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "stats_path", "type": "text", "label": "Stats Path", "default": "/_stats"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8443, Non-TLS: 8080. traffic_cop / traffic_cop"},
]


def authenticate(form_data):
    """
    Attempt to connect to Apache Traffic Server stats endpoint.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    stats_port = form_data.get('stats_port', '').strip()
    use_https = form_data.get('use_https', False)
    stats_path = form_data.get('stats_path', '/_stats').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = stats_port if stats_port else "8080"
        url = f"{scheme}://{host}:{port_num}{stats_path}"
        
        response = requests.get(url, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            # Try to parse stats
            data = response.json() if 'json' in response.headers.get('Content-Type', '') else {}
            
            # Extract key metrics
            version = data.get('global', {}).get('proxy.process.version.server.short', 'unknown')
            uptime = data.get('global', {}).get('proxy.node.restarts.proxy.start_time', 'unknown')
            
            return True, f"Successfully connected to Apache Traffic Server at {host}:{port_num}\nVersion: {version}"
        elif response.status_code == 403:
            return False, "Access forbidden - check stats authorization"
        elif response.status_code == 404:
            return False, f"Stats endpoint not found at {stats_path}"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Traffic Server error: {e}"

