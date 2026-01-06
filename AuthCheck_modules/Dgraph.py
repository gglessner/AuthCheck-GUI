# Dgraph Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Dgraph (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Dgraph Host"},
    {"name": "port", "type": "text", "label": "HTTP Port", "default": "8080",
     "port_toggle": "use_ssl", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "grpc_port", "type": "text", "label": "gRPC Port", "default": "9080",
     "port_toggle": "use_ssl", "tls_port": "9443", "non_tls_port": "9080"},
    {"name": "api_key", "type": "password", "label": "API Key (Cloud)"},
    {"name": "acl_token", "type": "password", "label": "ACL Token (Enterprise)"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8443/9443, Non-TLS: 8080/9080. ACL requires Enterprise."},
]


def authenticate(form_data):
    """Attempt to authenticate to Dgraph."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8080').strip()
    api_key = form_data.get('api_key', '').strip()
    acl_token = form_data.get('acl_token', '').strip()
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "Dgraph Host is required"
    
    try:
        scheme = "https" if use_ssl else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        headers = {'Content-Type': 'application/json'}
        if api_key:
            headers['Dg-Auth'] = api_key
        elif acl_token:
            headers['X-Dgraph-AccessToken'] = acl_token
        
        # Health check
        health_resp = requests.get(
            f"{base_url}/health",
            headers=headers,
            timeout=15
        )
        
        if health_resp.status_code == 200:
            health = health_resp.json()
            version = health[0].get('version', 'unknown') if isinstance(health, list) else health.get('version', 'unknown')
            
            # Get state
            state_resp = requests.get(
                f"{base_url}/state",
                headers=headers,
                timeout=10
            )
            groups = 0
            tablets = 0
            if state_resp.status_code == 200:
                state = state_resp.json()
                groups = len(state.get('groups', {}))
                for g in state.get('groups', {}).values():
                    tablets += len(g.get('tablets', {}))
            
            # Get schema predicates
            schema_resp = requests.post(
                f"{base_url}/query",
                headers=headers,
                json={'query': 'schema {}'},
                timeout=10
            )
            predicates = 0
            if schema_resp.status_code == 200:
                schema_data = schema_resp.json().get('data', {}).get('schema', [])
                predicates = len(schema_data)
            
            return True, f"Successfully connected to Dgraph\nHost: {host}:{port}\nVersion: {version}\nGroups: {groups}, Tablets: {tablets}\nPredicates: {predicates}"
        elif health_resp.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {health_resp.status_code}: {health_resp.text[:200]}"
            
    except Exception as e:
        return False, f"Dgraph error: {e}"

