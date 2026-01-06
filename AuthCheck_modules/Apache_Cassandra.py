# Apache Cassandra Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Cassandra (DB)"

form_fields = [
    {"name": "hosts", "type": "text", "label": "Contact Points", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "9042",
     "port_toggle": "use_ssl", "tls_port": "9142", "non_tls_port": "9042"},
    {"name": "keyspace", "type": "text", "label": "Keyspace"},
    {"name": "use_ssl", "type": "checkbox", "label": "Enable SSL/TLS"},
    {"name": "username", "type": "text", "label": "Username", "default": "cassandra"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "ssl_ca", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "ssl_cert", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "ssl_key", "type": "file", "label": "Client Key", "filter": "Key Files (*.pem *.key);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 9142, Non-TLS: 9042. cassandra / cassandra"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Cassandra.
    """
    try:
        from cassandra.cluster import Cluster
        from cassandra.auth import PlainTextAuthProvider
        from cassandra.policies import RoundRobinPolicy
    except ImportError:
        return False, "cassandra-driver package not installed. Run: pip install cassandra-driver"
    
    hosts = form_data.get('hosts', '').strip()
    port = form_data.get('port', '').strip()
    keyspace = form_data.get('keyspace', '').strip()
    use_ssl = form_data.get('use_ssl', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    ssl_ca = form_data.get('ssl_ca', '').strip()
    ssl_cert = form_data.get('ssl_cert', '').strip()
    ssl_key = form_data.get('ssl_key', '').strip()
    
    if not hosts:
        return False, "Contact Points is required"
    
    try:
        contact_points = [h.strip() for h in hosts.split(',')]
        port_num = int(port) if port else 9042
        
        auth_provider = None
        if username:
            auth_provider = PlainTextAuthProvider(username=username, password=password)
        
        ssl_options = None
        if use_ssl:
            import ssl
            ssl_context = ssl.create_default_context()
            if ssl_ca:
                ssl_context.load_verify_locations(ssl_ca)
            if ssl_cert and ssl_key:
                ssl_context.load_cert_chain(ssl_cert, ssl_key)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            ssl_options = {'ssl_context': ssl_context}
        
        cluster = Cluster(
            contact_points=contact_points,
            port=port_num,
            auth_provider=auth_provider,
            ssl_options=ssl_options,
            load_balancing_policy=RoundRobinPolicy(),
            connect_timeout=10
        )
        
        session = cluster.connect(keyspace if keyspace else None)
        
        # Get cluster info
        row = session.execute("SELECT release_version, cluster_name FROM system.local").one()
        version = row.release_version
        cluster_name = row.cluster_name
        
        session.shutdown()
        cluster.shutdown()
        
        ks_info = f" (keyspace: {keyspace})" if keyspace else ""
        return True, f"Successfully authenticated to Cassandra cluster '{cluster_name}' v{version}{ks_info}"
        
    except Exception as e:
        error_msg = str(e)
        if "AuthenticationFailed" in error_msg or "Bad credentials" in error_msg:
            return False, "Authentication failed: Invalid credentials"
        return False, f"Cassandra error: {e}"

