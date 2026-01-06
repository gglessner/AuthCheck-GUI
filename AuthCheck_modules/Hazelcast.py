# Hazelcast Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Hazelcast (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "5701",
     "port_toggle": "use_ssl", "tls_port": "5702", "non_tls_port": "5701"},
    {"name": "cluster_name", "type": "text", "label": "Cluster Name", "default": "dev"},
    {"name": "use_ssl", "type": "checkbox", "label": "Enable SSL"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 5702, Non-TLS: 5701. Cluster: dev. Enterprise: admin / hazelcast"},
]


def authenticate(form_data):
    """Attempt to authenticate to Hazelcast cluster."""
    try:
        import hazelcast
    except ImportError:
        return False, "hazelcast-python-client not installed. Run: pip install hazelcast-python-client"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '5701').strip()
    cluster_name = form_data.get('cluster_name', 'dev').strip()
    use_ssl = form_data.get('use_ssl', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    if not host:
        return False, "Host is required"
    
    try:
        port_num = int(port) if port else 5701
        
        config = {
            'cluster_name': cluster_name,
            'cluster_members': [f"{host}:{port_num}"],
            'connection_timeout': 10,
        }
        
        if use_ssl:
            config['ssl_enabled'] = True
        
        if username:
            config['creds_username'] = username
            config['creds_password'] = password
        
        client = hazelcast.HazelcastClient(**config)
        
        # Get cluster info
        cluster = client.cluster
        members = cluster.get_members()
        
        client.shutdown()
        
        member_info = [f"{m.address}" for m in members]
        
        return True, f"Successfully connected to Hazelcast cluster '{cluster_name}'\nMembers: {member_info}"
        
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower():
            return False, f"Authentication failed: {e}"
        return False, f"Hazelcast error: {e}"

