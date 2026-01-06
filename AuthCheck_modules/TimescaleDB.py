# TimescaleDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "TimescaleDB (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "5432"},
    {"name": "database", "type": "text", "label": "Database", "default": "postgres"},
    {"name": "username", "type": "text", "label": "Username", "default": "postgres"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "ssl_mode", "type": "combo", "label": "SSL Mode", "options": ["disable", "require", "verify-ca", "verify-full"], "default": "disable"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "postgres / (set during install). TimescaleDB extends PostgreSQL on port 5432."},
]


def authenticate(form_data):
    """Attempt to authenticate to TimescaleDB."""
    try:
        import psycopg2
    except ImportError:
        return False, "psycopg2 package not installed. Run: pip install psycopg2-binary"
    
    host = form_data.get('host', 'localhost').strip()
    port = form_data.get('port', '5432').strip()
    database = form_data.get('database', 'postgres').strip()
    username = form_data.get('username', 'postgres').strip()
    password = form_data.get('password', '')
    ssl_mode = form_data.get('ssl_mode', 'disable')
    
    if not host:
        return False, "Host is required"
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
        
        # Check if TimescaleDB is installed
        cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'timescaledb'")
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False, "Connected to PostgreSQL, but TimescaleDB extension not found"
        
        timescale_version = row[0]
        
        # Get PostgreSQL version
        cursor.execute("SELECT version()")
        pg_version = cursor.fetchone()[0].split(',')[0]
        
        # Get hypertable count
        cursor.execute("SELECT COUNT(*) FROM timescaledb_information.hypertables")
        hypertable_count = cursor.fetchone()[0]
        
        # Get continuous aggregate count
        try:
            cursor.execute("SELECT COUNT(*) FROM timescaledb_information.continuous_aggregates")
            cagg_count = cursor.fetchone()[0]
        except:
            cagg_count = 0
        
        conn.close()
        
        return True, f"Successfully authenticated to TimescaleDB {timescale_version}\n{pg_version}\nHypertables: {hypertable_count}\nContinuous Aggregates: {cagg_count}"
        
    except Exception as e:
        return False, f"TimescaleDB error: {e}"

