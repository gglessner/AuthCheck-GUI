# Milvus Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Milvus (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Milvus Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "19530"},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password", "default": "Milvus"},
    {"name": "token", "type": "password", "label": "Token (Zilliz Cloud)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: root/Milvus. Port 19530. Vector database for AI."},
]


def authenticate(form_data):
    """Attempt to authenticate to Milvus."""
    try:
        from pymilvus import connections, utility
    except ImportError:
        return False, "pymilvus package not installed. Run: pip install pymilvus"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '19530').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    token = form_data.get('token', '').strip()
    
    if not host:
        return False, "Milvus Host is required"
    
    try:
        conn_params = {
            'alias': 'authcheck',
            'host': host,
            'port': port
        }
        
        if token:
            conn_params['token'] = token
        elif username:
            conn_params['user'] = username
            conn_params['password'] = password
        
        connections.connect(**conn_params)
        
        # Get server version
        version = utility.get_server_version()
        
        # List collections
        collections = utility.list_collections()
        
        connections.disconnect('authcheck')
        
        return True, f"Successfully authenticated to Milvus\nHost: {host}:{port}\nVersion: {version}\nCollections: {len(collections)}\nSample: {', '.join(collections[:5]) if collections else 'none'}"
        
    except Exception as e:
        try:
            connections.disconnect('authcheck')
        except:
            pass
        return False, f"Milvus error: {e}"

