# Temporal Workflow Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Temporal Workflow (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "grpc_port", "type": "text", "label": "gRPC Port", "default": "7233",
     "port_toggle": "use_tls", "tls_port": "7233", "non_tls_port": "7233"},
    {"name": "web_port", "type": "text", "label": "Web UI Port", "default": "8080",
     "port_toggle": "use_tls", "tls_port": "443", "non_tls_port": "8080"},
    {"name": "namespace", "type": "text", "label": "Namespace", "default": "default"},
    {"name": "use_tls", "type": "checkbox", "label": "Use TLS"},
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "gRPC: 7233 (both). Web: 443 (TLS), 8080 (non-TLS). Default: no auth."},
]


def authenticate(form_data):
    """Attempt to connect to Temporal."""
    host = form_data.get('host', '').strip()
    grpc_port = form_data.get('grpc_port', '7233').strip()
    web_port = form_data.get('web_port', '8080').strip()
    namespace = form_data.get('namespace', 'default').strip()
    use_tls = form_data.get('use_tls', False)
    api_key = form_data.get('api_key', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    # Try Web UI API first
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    try:
        scheme = "https" if use_tls else "http"
        base_url = f"{scheme}://{host}:{web_port}/api/v1"
        
        headers = {}
        if api_key:
            headers['Authorization'] = f"Bearer {api_key}"
        
        # Get cluster info
        response = requests.get(f"{base_url}/cluster-info", headers=headers,
                               verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            cluster_name = data.get('clusterName', 'unknown')
            
            # Get namespaces
            ns_resp = requests.get(f"{base_url}/namespaces", headers=headers,
                                  verify=verify_ssl, timeout=10)
            namespaces = []
            if ns_resp.status_code == 200:
                ns_data = ns_resp.json()
                namespaces = [n.get('namespaceInfo', {}).get('name') 
                             for n in ns_data.get('namespaces', [])]
            
            return True, f"Successfully connected to Temporal cluster '{cluster_name}'\nNamespaces: {namespaces}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API key"
        else:
            # Try without API to check if accessible
            health_resp = requests.get(f"{scheme}://{host}:{web_port}/", 
                                       verify=verify_ssl, timeout=10)
            if health_resp.status_code == 200:
                return True, f"Temporal Web UI accessible at {host}:{web_port}"
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, f"Temporal error: {e}"

