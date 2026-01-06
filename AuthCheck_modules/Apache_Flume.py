# Apache Flume Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Flume (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Agent Host", "default": "localhost"},
    {"name": "metrics_port", "type": "text", "label": "Metrics Port", "default": "41414",
     "port_toggle": "use_https", "tls_port": "41414", "non_tls_port": "41414"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Metrics: 41414 (TLS/non-TLS same). No auth typically."},
]


def authenticate(form_data):
    """
    Attempt to connect to Apache Flume agent metrics endpoint.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    metrics_port = form_data.get('metrics_port', '').strip()
    use_https = form_data.get('use_https', False)
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Agent Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = metrics_port if metrics_port else "41414"
        base_url = f"{scheme}://{host}:{port_num}"
        
        # Get metrics
        url = f"{base_url}/metrics"
        response = requests.get(url, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Parse component info
            sources = []
            channels = []
            sinks = []
            
            for key, value in data.items():
                if key.startswith('SOURCE.'):
                    sources.append(key.replace('SOURCE.', ''))
                elif key.startswith('CHANNEL.'):
                    channels.append(key.replace('CHANNEL.', ''))
                elif key.startswith('SINK.'):
                    sinks.append(key.replace('SINK.', ''))
            
            return True, f"Successfully connected to Apache Flume at {host}:{port_num}\nSources: {sources}\nChannels: {channels}\nSinks: {sinks}"
        elif response.status_code == 404:
            return False, "Metrics endpoint not found (ensure http.enabled=true in Flume config)"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Flume error: {e}"

