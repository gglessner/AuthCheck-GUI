# MongoDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "MongoDB (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "27017",
     "port_toggle": "use_tls", "tls_port": "27017", "non_tls_port": "27017"},
    {"name": "database", "type": "text", "label": "Auth Database", "default": "admin"},
    {"name": "use_tls", "type": "checkbox", "label": "Enable TLS"},
    {"name": "auth_mechanism", "type": "combo", "label": "Auth Mechanism",
     "options": ["DEFAULT", "SCRAM-SHA-1", "SCRAM-SHA-256", "MONGODB-X509", "PLAIN"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "tls_ca", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "tls_cert", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "replica_set", "type": "text", "label": "Replica Set"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 27017 (TLS/non-TLS same). Default: no auth. admin / admin"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to MongoDB.
    """
    try:
        from pymongo import MongoClient
        from pymongo.errors import OperationFailure, ConnectionFailure
    except ImportError:
        return False, "pymongo package not installed. Run: pip install pymongo"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    database = form_data.get('database', 'admin').strip()
    use_tls = form_data.get('use_tls', False)
    auth_mechanism = form_data.get('auth_mechanism', 'DEFAULT')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    tls_ca = form_data.get('tls_ca', '').strip()
    tls_cert = form_data.get('tls_cert', '').strip()
    replica_set = form_data.get('replica_set', '').strip()
    
    if not host:
        return False, "Host is required"
    
    try:
        port_num = int(port) if port else 27017
        
        # Build connection URI
        if username and password:
            from urllib.parse import quote_plus
            uri = f"mongodb://{quote_plus(username)}:{quote_plus(password)}@{host}:{port_num}/{database}"
        else:
            uri = f"mongodb://{host}:{port_num}/{database}"
        
        client_kwargs = {
            'serverSelectionTimeoutMS': 10000,
            'connectTimeoutMS': 10000,
        }
        
        if auth_mechanism and auth_mechanism != "DEFAULT":
            client_kwargs['authMechanism'] = auth_mechanism
        
        if use_tls:
            client_kwargs['tls'] = True
            if tls_ca:
                client_kwargs['tlsCAFile'] = tls_ca
            if tls_cert:
                client_kwargs['tlsCertificateKeyFile'] = tls_cert
            client_kwargs['tlsAllowInvalidCertificates'] = not tls_ca
        
        if replica_set:
            client_kwargs['replicaSet'] = replica_set
        
        client = MongoClient(uri, **client_kwargs)
        
        # Force connection and auth check
        server_info = client.server_info()
        version = server_info.get('version', 'unknown')
        
        client.close()
        
        return True, f"Successfully authenticated to MongoDB {version} at {host}:{port_num}"
        
    except OperationFailure as e:
        return False, f"Authentication failed: {e}"
    except ConnectionFailure as e:
        return False, f"Connection failed: {e}"
    except Exception as e:
        return False, f"MongoDB error: {e}"

