# JanusGraph Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "JanusGraph (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "JanusGraph Host"},
    {"name": "port", "type": "text", "label": "Gremlin Port", "default": "8182",
     "port_toggle": "use_ssl", "tls_port": "8182", "non_tls_port": "8182"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Gremlin: 8182 (TLS/non-TLS same). Graph DB on Cassandra/HBase."},
]


def authenticate(form_data):
    """Attempt to authenticate to JanusGraph."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8182').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "JanusGraph Host is required"
    
    try:
        scheme = "wss" if use_ssl else "ws"
        http_scheme = "https" if use_ssl else "http"
        base_url = f"{http_scheme}://{host}:{port}"
        
        auth = None
        if username:
            auth = (username, password)
        
        # Try HTTP endpoint first
        response = requests.get(
            f"{base_url}/",
            auth=auth,
            timeout=15,
            verify=not use_ssl
        )
        
        if response.status_code == 200:
            # Try Gremlin query via HTTP
            gremlin_resp = requests.post(
                f"{base_url}",
                json={'gremlin': 'g.V().count()'},
                auth=auth,
                timeout=10,
                verify=not use_ssl
            )
            
            vertex_count = 0
            if gremlin_resp.status_code == 200:
                data = gremlin_resp.json()
                if 'result' in data and 'data' in data['result']:
                    vertex_count = data['result']['data'].get('@value', [{}])[0].get('@value', 0) if data['result']['data'] else 0
            
            return True, f"Successfully connected to JanusGraph\nHost: {host}:{port}\nGremlin Server: Connected\nVertex Count: {vertex_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            # Just try to connect
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, int(port)))
            sock.close()
            
            if result == 0:
                return True, f"Successfully connected to JanusGraph\nHost: {host}:{port}\nGremlin port is accessible"
            else:
                return False, f"Cannot connect to {host}:{port}"
            
    except Exception as e:
        return False, f"JanusGraph error: {e}"

