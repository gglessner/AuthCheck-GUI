# Chroma Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Chroma (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Chroma Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "8000",
     "port_toggle": "use_ssl", "tls_port": "443", "non_tls_port": "8000"},
    {"name": "api_key", "type": "password", "label": "API Key (if configured)"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 443, Non-TLS: 8000. Vector database. No auth by default."},
]


def authenticate(form_data):
    """Attempt to authenticate to Chroma."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8000').strip()
    api_key = form_data.get('api_key', '').strip()
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "Chroma Host is required"
    
    try:
        scheme = "https" if use_ssl else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        headers = {'Accept': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        # Get version
        response = requests.get(
            f"{base_url}/api/v1/version",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            version = response.text.strip().strip('"')
            
            # Get collections
            colls_resp = requests.get(
                f"{base_url}/api/v1/collections",
                headers=headers,
                timeout=10
            )
            coll_count = 0
            coll_names = []
            if colls_resp.status_code == 200:
                colls = colls_resp.json()
                coll_count = len(colls)
                coll_names = [c.get('name', 'unknown') for c in colls[:5]]
            
            # Get heartbeat
            heartbeat_resp = requests.get(
                f"{base_url}/api/v1/heartbeat",
                headers=headers,
                timeout=5
            )
            heartbeat = ""
            if heartbeat_resp.status_code == 200:
                heartbeat = f"\nHeartbeat: {heartbeat_resp.json().get('nanosecond heartbeat', 'ok')}"
            
            return True, f"Successfully authenticated to Chroma\nHost: {host}:{port}\nVersion: {version}\nCollections: {coll_count}{heartbeat}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API key"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Chroma error: {e}"

