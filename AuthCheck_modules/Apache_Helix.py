# Apache Helix Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Helix (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Controller Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "REST Port", "default": "8100",
     "port_toggle": "use_https", "tls_port": "8100", "non_tls_port": "8100"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "cluster_name", "type": "text", "label": "Cluster Name"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "REST: 8100 (TLS/non-TLS same). Default: no auth (ZK-based)"},
]


def authenticate(form_data):
    """
    Attempt to connect to Apache Helix REST API.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    cluster_name = form_data.get('cluster_name', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Controller Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "8100"
        base_url = f"{scheme}://{host}:{port_num}/admin/v2"
        
        # Get clusters
        url = f"{base_url}/clusters"
        response = requests.get(url, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            clusters = data.get('clusters', [])
            
            # If specific cluster provided, get its info
            if cluster_name and cluster_name in clusters:
                cluster_url = f"{base_url}/clusters/{cluster_name}"
                cluster_response = requests.get(cluster_url, verify=verify_ssl, timeout=10)
                if cluster_response.status_code == 200:
                    cluster_data = cluster_response.json()
                    resources = cluster_data.get('resources', [])
                    instances = cluster_data.get('liveInstances', [])
                    return True, f"Successfully connected to Apache Helix at {host}:{port_num}\nCluster: {cluster_name}\nResources: {len(resources)}, Live Instances: {len(instances)}"
            
            return True, f"Successfully connected to Apache Helix at {host}:{port_num}\nClusters: {clusters}"
        elif response.status_code == 404:
            return False, "Helix REST API not found"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Helix error: {e}"

