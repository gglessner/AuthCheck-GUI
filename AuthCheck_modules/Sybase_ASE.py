# SAP/Sybase ASE Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "SAP/Sybase ASE (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "ASE Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "5000"},
    {"name": "database", "type": "text", "label": "Database", "default": "master"},
    {"name": "username", "type": "text", "label": "Username", "default": "sa"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "sa / (set during install). Default port 5000. Uses TDS protocol."},
]


def authenticate(form_data):
    """Attempt to authenticate to SAP/Sybase ASE."""
    try:
        import pymssql
    except ImportError:
        try:
            import sybpydb
            use_sybpydb = True
        except ImportError:
            return False, "pymssql or sybpydb package not installed. Run: pip install pymssql"
        use_sybpydb = True
    else:
        use_sybpydb = False
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '5000').strip()
    database = form_data.get('database', 'master').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    if not host:
        return False, "ASE Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        if use_sybpydb:
            conn = sybpydb.connect(
                servername=host,
                user=username,
                password=password,
                database=database
            )
        else:
            # pymssql can connect to Sybase with TDS
            conn = pymssql.connect(
                server=host,
                port=int(port),
                user=username,
                password=password,
                database=database,
                tds_version='5.0'  # Sybase TDS version
            )
        
        cursor = conn.cursor()
        
        # Get version
        cursor.execute("SELECT @@version")
        version = cursor.fetchone()[0].split('\n')[0]
        
        # Get server name
        cursor.execute("SELECT @@servername")
        server_name = cursor.fetchone()[0]
        
        # Get database count
        cursor.execute("SELECT COUNT(*) FROM master..sysdatabases")
        db_count = cursor.fetchone()[0]
        
        conn.close()
        return True, f"Successfully authenticated to Sybase ASE\nServer: {server_name}\nVersion: {version}\nDatabases: {db_count}"
        
    except Exception as e:
        return False, f"Sybase ASE error: {e}"

