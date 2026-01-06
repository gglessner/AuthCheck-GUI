# RethinkDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "RethinkDB (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "RethinkDB Host"},
    {"name": "port", "type": "text", "label": "Driver Port", "default": "28015"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: admin/(blank). Driver port 28015, Web UI 8080."},
]


def authenticate(form_data):
    """Attempt to authenticate to RethinkDB."""
    try:
        from rethinkdb import r
    except ImportError:
        return False, "rethinkdb package not installed. Run: pip install rethinkdb"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '28015').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    if not host:
        return False, "RethinkDB Host is required"
    
    try:
        conn_args = {
            'host': host,
            'port': int(port)
        }
        
        if username:
            conn_args['user'] = username
            conn_args['password'] = password
        
        conn = r.connect(**conn_args)
        
        # Get server info
        server_info = r.db('rethinkdb').table('server_config').run(conn)
        servers = list(server_info)
        
        # Get databases
        databases = list(r.db_list().run(conn))
        
        # Get cluster status
        status = list(r.db('rethinkdb').table('server_status').run(conn))
        
        conn.close()
        
        return True, f"Successfully authenticated to RethinkDB\nHost: {host}:{port}\nServers: {len(servers)}\nDatabases: {len(databases)}\nSample: {', '.join(databases[:5]) if databases else 'none'}"
        
    except Exception as e:
        return False, f"RethinkDB error: {e}"

