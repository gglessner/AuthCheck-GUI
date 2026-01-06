# Logstash Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Logstash (Logging)"

form_fields = [
    {"name": "host", "type": "text", "label": "Logstash Host"},
    {"name": "port", "type": "text", "label": "API Port", "default": "9600",
     "port_toggle": "use_ssl", "tls_port": "9600", "non_tls_port": "9600"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API: 9600, Beats: 5044/5045 (TLS/non-TLS same). X-Pack auth."},
]


def authenticate(form_data):
    """Attempt to authenticate to Logstash."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '9600').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "Logstash Host is required"
    
    try:
        scheme = "https" if use_ssl else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        auth = None
        if username:
            auth = (username, password)
        
        # Get node info
        response = requests.get(
            f"{base_url}/",
            auth=auth,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('version', 'unknown')
            host_name = data.get('host', 'unknown')
            status = data.get('status', 'unknown')
            
            # Get pipeline stats
            stats_resp = requests.get(
                f"{base_url}/_node/stats/pipelines",
                auth=auth,
                timeout=10
            )
            pipeline_info = ""
            if stats_resp.status_code == 200:
                stats = stats_resp.json()
                pipelines = stats.get('pipelines', {})
                pipeline_count = len(pipelines)
                pipeline_names = list(pipelines.keys())[:3]
                pipeline_info = f"\nPipelines: {pipeline_count}\nSample: {', '.join(pipeline_names) if pipeline_names else 'none'}"
            
            return True, f"Successfully authenticated to Logstash\nHost: {host_name}\nVersion: {version}\nStatus: {status}{pipeline_info}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Logstash error: {e}"

