# Apache Tika Server Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Tika (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "9998",
     "port_toggle": "use_https", "tls_port": "9998", "non_tls_port": "9998"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 9998 (TLS/non-TLS same). Default: no auth."},
]


def authenticate(form_data):
    """
    Attempt to connect to Apache Tika Server.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "9998"
        base_url = f"{scheme}://{host}:{port_num}"
        
        # Get Tika version
        url = f"{base_url}/version"
        response = requests.get(url, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            version = response.text.strip()
            
            # Get available parsers
            parsers_url = f"{base_url}/parsers"
            parsers_response = requests.get(parsers_url, headers={"Accept": "application/json"}, verify=verify_ssl, timeout=10)
            parser_count = 0
            if parsers_response.status_code == 200:
                parsers_data = parsers_response.json()
                parser_count = len(parsers_data.get('name', []) if isinstance(parsers_data, dict) else parsers_data)
            
            # Get available detectors
            detectors_url = f"{base_url}/detectors"
            detectors_response = requests.get(detectors_url, headers={"Accept": "application/json"}, verify=verify_ssl, timeout=10)
            detector_count = 0
            if detectors_response.status_code == 200:
                detectors_data = detectors_response.json()
                detector_count = len(detectors_data.get('name', []) if isinstance(detectors_data, dict) else detectors_data)
            
            return True, f"Successfully connected to Apache Tika Server\nVersion: {version}\nParsers: {parser_count}, Detectors: {detector_count}"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Tika error: {e}"

