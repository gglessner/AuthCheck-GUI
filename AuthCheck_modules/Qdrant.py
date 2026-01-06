# Qdrant Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Qdrant (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Qdrant Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "6333",
     "port_toggle": "use_ssl", "tls_port": "6333", "non_tls_port": "6333"},
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "HTTP: 6333, gRPC: 6334 (TLS/non-TLS same). API key for Cloud."},
]


def authenticate(form_data):
    """Attempt to authenticate to Qdrant."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '6333').strip()
    api_key = form_data.get('api_key', '').strip()
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "Qdrant Host is required"
    
    try:
        scheme = "https" if use_ssl else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        headers = {'Accept': 'application/json'}
        if api_key:
            headers['api-key'] = api_key
        
        # Get cluster info
        response = requests.get(
            f"{base_url}/",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            info = response.json()
            version = info.get('version', 'unknown')
            
            # Get collections
            colls_resp = requests.get(
                f"{base_url}/collections",
                headers=headers,
                timeout=10
            )
            coll_count = 0
            coll_names = []
            if colls_resp.status_code == 200:
                colls = colls_resp.json().get('result', {}).get('collections', [])
                coll_count = len(colls)
                coll_names = [c.get('name', 'unknown') for c in colls[:5]]
            
            return True, f"Successfully authenticated to Qdrant\nHost: {host}:{port}\nVersion: {version}\nCollections: {coll_count}\nSample: {', '.join(coll_names) if coll_names else 'none'}"
        elif response.status_code == 401 or response.status_code == 403:
            return False, "Authentication failed: Invalid API key"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Qdrant error: {e}"

