# Greenplum Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Greenplum (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Master Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "5432"},
    {"name": "database", "type": "text", "label": "Database", "default": "postgres"},
    {"name": "username", "type": "text", "label": "Username", "default": "gpadmin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "ssl_mode", "type": "combo", "label": "SSL Mode", "options": ["disable", "require", "verify-ca", "verify-full"], "default": "disable"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "gpadmin / (set during install). Uses PostgreSQL protocol on port 5432."},
]


def authenticate(form_data):
    """Attempt to authenticate to Greenplum."""
    try:
        import psycopg2
    except ImportError:
        return False, "psycopg2 package not installed. Run: pip install psycopg2-binary"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '5432').strip()
    database = form_data.get('database', 'postgres').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    ssl_mode = form_data.get('ssl_mode', 'disable')
    
    if not host:
        return False, "Master Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=int(port),
            database=database,
            user=username,
            password=password,
            sslmode=ssl_mode,
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        
        # Get version - check if it's Greenplum
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        if 'Greenplum' not in version:
            conn.close()
            return False, "Connected to PostgreSQL, but not Greenplum"
        
        # Get segment count
        cursor.execute("SELECT COUNT(*) FROM gp_segment_configuration WHERE role = 'p' AND content >= 0")
        segment_count = cursor.fetchone()[0]
        
        # Get current user and database
        cursor.execute("SELECT current_user, current_database()")
        row = cursor.fetchone()
        current_user = row[0]
        current_db = row[1]
        
        conn.close()
        gp_version = version.split('(')[0].strip()
        return True, f"Successfully authenticated to {gp_version}\nUser: {current_user}\nDatabase: {current_db}\nPrimary Segments: {segment_count}"
        
    except Exception as e:
        return False, f"Greenplum error: {e}"

