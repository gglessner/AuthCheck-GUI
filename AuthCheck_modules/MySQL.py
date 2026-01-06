# MySQL/MariaDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "MySQL / MariaDB (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "3306",
     "port_toggle": "use_ssl", "tls_port": "3306", "non_tls_port": "3306"},
    {"name": "database", "type": "text", "label": "Database"},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "use_ssl", "type": "checkbox", "label": "Enable SSL/TLS"},
    {"name": "ssl_verify", "type": "checkbox", "label": "Verify Server Certificate"},
    {"name": "ssl_ca", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "ssl_cert", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "ssl_key", "type": "file", "label": "Client Key", "filter": "Key Files (*.pem *.key);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 3306 (TLS/non-TLS same). root / (empty), root / mysql"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to MySQL/MariaDB.
    
    Args:
        form_data (dict): Form field values
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        import mysql.connector
    except ImportError:
        try:
            import pymysql
            mysql_module = pymysql
        except ImportError:
            return False, "mysql-connector-python or pymysql not installed. Run: pip install mysql-connector-python"
        else:
            mysql_module = None
    else:
        mysql_module = mysql.connector
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    database = form_data.get('database', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    use_ssl = form_data.get('use_ssl', False)
    ssl_verify = form_data.get('ssl_verify', False)
    ssl_ca = form_data.get('ssl_ca', '').strip()
    ssl_cert = form_data.get('ssl_cert', '').strip()
    ssl_key = form_data.get('ssl_key', '').strip()
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        conn_params = {
            'host': host,
            'port': int(port) if port else 3306,
            'user': username,
            'password': password,
            'connection_timeout': 10,
        }
        
        if database:
            conn_params['database'] = database
        
        if use_ssl:
            ssl_config = {}
            if ssl_ca:
                ssl_config['ca'] = ssl_ca
            if ssl_cert:
                ssl_config['cert'] = ssl_cert
            if ssl_key:
                ssl_config['key'] = ssl_key
            if not ssl_verify:
                ssl_config['verify_cert'] = False
                ssl_config['verify_identity'] = False
            
            if mysql_module == mysql.connector:
                conn_params['ssl_ca'] = ssl_ca if ssl_ca else None
                conn_params['ssl_cert'] = ssl_cert if ssl_cert else None
                conn_params['ssl_key'] = ssl_key if ssl_key else None
                conn_params['ssl_verify_cert'] = ssl_verify
            else:
                conn_params['ssl'] = ssl_config if ssl_config else True
        
        conn = mysql_module.connect(**conn_params)
        
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION(), DATABASE(), USER()")
        version, current_db, current_user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        db_info = f"Database: {current_db}" if current_db else "No database selected"
        return True, f"Successfully authenticated to MySQL/MariaDB\n{db_info}\nUser: {current_user}\nVersion: {version}"
        
    except mysql_module.Error as e:
        error_code = e.args[0] if e.args else None
        error_codes = {
            1045: "Access denied - invalid username or password",
            1049: "Unknown database",
            2003: "Cannot connect to server - check host and port",
            2005: "Unknown host",
            2006: "Server has gone away",
        }
        if error_code in error_codes:
            return False, f"MySQL error {error_code}: {error_codes[error_code]}"
        return False, f"MySQL error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

