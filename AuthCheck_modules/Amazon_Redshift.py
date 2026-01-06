# Amazon Redshift Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Amazon Redshift (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Cluster Endpoint"},
    {"name": "port", "type": "text", "label": "Port", "default": "5439",
     "port_toggle": "ssl_mode", "tls_port": "5439", "non_tls_port": "5439"},
    {"name": "database", "type": "text", "label": "Database", "default": "dev"},
    {"name": "username", "type": "text", "label": "Username", "default": "awsuser"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "ssl_mode", "type": "combo", "label": "SSL Mode", "options": ["require", "verify-ca", "verify-full", "disable"], "default": "require"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 5439 (TLS/non-TLS same). awsuser / (set on creation)."},
]


def authenticate(form_data):
    """Attempt to authenticate to Amazon Redshift."""
    try:
        import redshift_connector
    except ImportError:
        try:
            import psycopg2
            use_psycopg2 = True
        except ImportError:
            return False, "redshift_connector or psycopg2 package not installed. Run: pip install redshift-connector"
        use_psycopg2 = True
    else:
        use_psycopg2 = False
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '5439').strip()
    database = form_data.get('database', 'dev').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    ssl_mode = form_data.get('ssl_mode', 'require')
    
    if not host:
        return False, "Cluster Endpoint is required"
    if not username:
        return False, "Username is required"
    
    try:
        if use_psycopg2:
            import psycopg2
            conn = psycopg2.connect(
                host=host,
                port=int(port),
                database=database,
                user=username,
                password=password,
                sslmode=ssl_mode,
                connect_timeout=10
            )
        else:
            conn = redshift_connector.connect(
                host=host,
                port=int(port),
                database=database,
                user=username,
                password=password,
                ssl=ssl_mode != 'disable'
            )
        
        cursor = conn.cursor()
        
        # Get version
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0].split(',')[0]
        
        # Get current user and database
        cursor.execute("SELECT current_user, current_database()")
        row = cursor.fetchone()
        current_user = row[0]
        current_db = row[1]
        
        # Get node info
        cursor.execute("SELECT COUNT(*) FROM stv_slices")
        slice_count = cursor.fetchone()[0]
        
        conn.close()
        return True, f"Successfully authenticated to Amazon Redshift\n{version}\nUser: {current_user}\nDatabase: {current_db}\nSlices: {slice_count}"
        
    except Exception as e:
        return False, f"Redshift error: {e}"

