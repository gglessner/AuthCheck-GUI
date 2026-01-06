# Aerospike Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Aerospike (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Aerospike Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "3000",
     "port_toggle": "use_tls", "tls_port": "4333", "non_tls_port": "3000"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "use_tls", "type": "checkbox", "label": "Use TLS"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 4333, Non-TLS: 3000. Auth requires Enterprise. Key-value DB."},
]


def authenticate(form_data):
    """Attempt to authenticate to Aerospike."""
    try:
        import aerospike
    except ImportError:
        return False, "aerospike package not installed. Run: pip install aerospike"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '3000').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    use_tls = form_data.get('use_tls', False)
    
    if not host:
        return False, "Aerospike Host is required"
    
    try:
        config = {
            'hosts': [(host, int(port))]
        }
        
        if use_tls:
            config['tls'] = {'enable': True}
        
        if username:
            config['user'] = username
            config['password'] = password
        
        client = aerospike.client(config).connect()
        
        # Get cluster info
        info = client.info_all('namespaces')
        
        # Parse namespaces
        namespaces = set()
        for node, (err, data) in info.items():
            if not err:
                namespaces.update(data.strip().split(';'))
        
        # Get node count
        nodes = list(info.keys())
        
        client.close()
        
        return True, f"Successfully authenticated to Aerospike\nHost: {host}:{port}\nNodes: {len(nodes)}\nNamespaces: {len(namespaces)}\nSample: {', '.join(list(namespaces)[:5]) if namespaces else 'none'}"
        
    except Exception as e:
        return False, f"Aerospike error: {e}"

