# Google Cloud SQL Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Google Cloud SQL (Cloud)"

form_fields = [
    {"name": "host", "type": "text", "label": "Cloud SQL IP/Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "3306",
     "port_toggle": "use_ssl", "tls_port": "3306", "non_tls_port": "3306"},
    {"name": "db_type", "type": "combo", "label": "Database Type", "options": ["MySQL", "PostgreSQL", "SQL Server"], "default": "MySQL"},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "database", "type": "text", "label": "Database"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "MySQL: 3306, PG: 5432, MSSQL: 1433 (TLS/non-TLS same). Managed SQL."},
]


def authenticate(form_data):
    """Attempt to authenticate to Google Cloud SQL."""
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '3306').strip()
    db_type = form_data.get('db_type', 'MySQL')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    database = form_data.get('database', '').strip()
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "Cloud SQL IP/Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        if db_type == 'MySQL':
            try:
                import mysql.connector
            except ImportError:
                return False, "mysql-connector-python package not installed"
            
            conn_params = {
                'host': host,
                'port': int(port),
                'user': username,
                'password': password,
                'connection_timeout': 10
            }
            if database:
                conn_params['database'] = database
            if use_ssl:
                conn_params['ssl_disabled'] = False
            
            conn = mysql.connector.connect(**conn_params)
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            cursor.execute("SHOW DATABASES")
            databases = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            
            return True, f"Successfully authenticated to Cloud SQL (MySQL)\nHost: {host}:{port}\nVersion: {version}\nDatabases: {len(databases)}"
            
        elif db_type == 'PostgreSQL':
            try:
                import psycopg2
            except ImportError:
                return False, "psycopg2 package not installed"
            
            conn_params = {
                'host': host,
                'port': int(port),
                'user': username,
                'password': password,
                'connect_timeout': 10
            }
            if database:
                conn_params['dbname'] = database
            if use_ssl:
                conn_params['sslmode'] = 'require'
            
            conn = psycopg2.connect(**conn_params)
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
            databases = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            
            return True, f"Successfully authenticated to Cloud SQL (PostgreSQL)\nHost: {host}:{port}\nVersion: {version[:60]}...\nDatabases: {len(databases)}"
            
        else:  # SQL Server
            try:
                import pymssql
            except ImportError:
                return False, "pymssql package not installed"
            
            conn = pymssql.connect(
                server=host,
                port=int(port),
                user=username,
                password=password,
                database=database or 'master',
                login_timeout=10
            )
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            cursor.execute("SELECT name FROM sys.databases")
            databases = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            
            return True, f"Successfully authenticated to Cloud SQL (SQL Server)\nHost: {host}:{port}\nVersion: {version[:60]}...\nDatabases: {len(databases)}"
            
    except Exception as e:
        return False, f"Cloud SQL error: {e}"

