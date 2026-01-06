# ScyllaDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "ScyllaDB (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "ScyllaDB Host"},
    {"name": "port", "type": "text", "label": "CQL Port", "default": "9042",
     "port_toggle": "use_ssl", "tls_port": "9142", "non_tls_port": "9042"},
    {"name": "username", "type": "text", "label": "Username", "default": "cassandra"},
    {"name": "password", "type": "password", "label": "Password", "default": "cassandra"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 9142, Non-TLS: 9042. cassandra / cassandra. Cassandra-compatible."},
]


def authenticate(form_data):
    """Attempt to authenticate to ScyllaDB."""
    try:
        from cassandra.cluster import Cluster
        from cassandra.auth import PlainTextAuthProvider
    except ImportError:
        return False, "cassandra-driver package not installed. Run: pip install cassandra-driver"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '9042').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "ScyllaDB Host is required"
    
    try:
        cluster_args = {
            'contact_points': [host],
            'port': int(port)
        }
        
        if username:
            auth_provider = PlainTextAuthProvider(username=username, password=password)
            cluster_args['auth_provider'] = auth_provider
        
        if use_ssl:
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            cluster_args['ssl_context'] = ssl_context
        
        cluster = Cluster(**cluster_args)
        session = cluster.connect()
        
        # Get cluster name and version
        row = session.execute("SELECT cluster_name, release_version FROM system.local").one()
        cluster_name = row.cluster_name
        version = row.release_version
        
        # Get keyspaces
        rows = session.execute("SELECT keyspace_name FROM system_schema.keyspaces")
        keyspaces = [row.keyspace_name for row in rows]
        
        # Get node count
        nodes = session.execute("SELECT peer FROM system.peers")
        node_count = len(list(nodes)) + 1  # +1 for connected node
        
        session.shutdown()
        cluster.shutdown()
        
        return True, f"Successfully authenticated to ScyllaDB\nHost: {host}:{port}\nCluster: {cluster_name}\nVersion: {version}\nNodes: {node_count}\nKeyspaces: {len(keyspaces)}"
        
    except Exception as e:
        return False, f"ScyllaDB error: {e}"
