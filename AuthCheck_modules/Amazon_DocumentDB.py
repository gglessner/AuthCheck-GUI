# Amazon DocumentDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Amazon DocumentDB (Cloud)"

form_fields = [
    {"name": "host", "type": "text", "label": "DocumentDB Endpoint"},
    {"name": "port", "type": "text", "label": "Port", "default": "27017",
     "port_toggle": "use_tls", "tls_port": "27017", "non_tls_port": "27017"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "database", "type": "text", "label": "Database", "default": "admin"},
    {"name": "use_tls", "type": "checkbox", "label": "Use TLS"},
    {"name": "ca_file", "type": "file", "label": "CA Certificate File", "file_filter": "PEM Files (*.pem)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 27017 (TLS required). Download rds-combined-ca-bundle.pem."},
]


def authenticate(form_data):
    """Attempt to authenticate to Amazon DocumentDB."""
    try:
        from pymongo import MongoClient
        from pymongo.errors import ConnectionFailure, OperationFailure
    except ImportError:
        return False, "pymongo package not installed. Run: pip install pymongo"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '27017').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    database = form_data.get('database', 'admin').strip()
    use_tls = form_data.get('use_tls', False)
    ca_file = form_data.get('ca_file', '').strip()
    
    if not host:
        return False, "DocumentDB Endpoint is required"
    if not username:
        return False, "Username is required"
    
    try:
        # Build connection string
        conn_str = f"mongodb://{username}:{password}@{host}:{port}/{database}"
        
        client_args = {
            'serverSelectionTimeoutMS': 10000,
            'directConnection': True
        }
        
        if use_tls:
            client_args['tls'] = True
            client_args['tlsAllowInvalidHostnames'] = True
            if ca_file:
                client_args['tlsCAFile'] = ca_file
        
        client = MongoClient(conn_str, **client_args)
        
        # Test connection
        server_info = client.server_info()
        version = server_info.get('version', 'unknown')
        
        # Get database list
        databases = client.list_database_names()
        
        client.close()
        
        return True, f"Successfully authenticated to Amazon DocumentDB\nHost: {host}:{port}\nVersion: {version}\nDatabases: {len(databases)}\nSample: {', '.join(databases[:5]) if databases else 'none'}"
        
    except OperationFailure as e:
        return False, f"Authentication failed: {e}"
    except ConnectionFailure as e:
        return False, f"Connection failed: {e}"
    except Exception as e:
        return False, f"Amazon DocumentDB error: {e}"

