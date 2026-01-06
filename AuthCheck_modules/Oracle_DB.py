# Oracle Database Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Oracle Database (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "1521"},
    {"name": "connection_type", "type": "combo", "label": "Connection Type",
     "options": ["Service Name", "SID", "TNS Alias"]},
    {"name": "service_name", "type": "text", "label": "Service Name / SID / TNS"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "auth_mode", "type": "combo", "label": "Authentication Mode",
     "options": ["Normal", "SYSDBA", "SYSOPER", "SYSASM", "SYSBACKUP", "SYSDG", "SYSKM"]},
    {"name": "wallet_location", "type": "file", "label": "Wallet Location", "filter": "Wallet Files (*.sso *.p12);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 1521 (or 2484 TCPS). sys / change_on_install, system / manager"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Oracle Database.
    
    Args:
        form_data (dict): Form field values
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        import oracledb
    except ImportError:
        try:
            import cx_Oracle as oracledb
        except ImportError:
            return False, "oracledb or cx_Oracle package not installed. Run: pip install oracledb"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    connection_type = form_data.get('connection_type', 'Service Name')
    service_name = form_data.get('service_name', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    auth_mode = form_data.get('auth_mode', 'Normal')
    wallet_location = form_data.get('wallet_location', '').strip()
    
    if not username:
        return False, "Username is required"
    if not service_name:
        return False, "Service Name / SID / TNS is required"
    
    try:
        # Build the DSN
        if connection_type == "TNS Alias":
            dsn = service_name
        elif connection_type == "SID":
            dsn = oracledb.makedsn(host, int(port), sid=service_name)
        else:  # Service Name
            dsn = oracledb.makedsn(host, int(port), service_name=service_name)
        
        # Determine auth mode
        mode = 0
        if hasattr(oracledb, 'AUTH_MODE_SYSDBA'):
            mode_map = {
                'SYSDBA': oracledb.AUTH_MODE_SYSDBA,
                'SYSOPER': oracledb.AUTH_MODE_SYSOPER,
            }
            if auth_mode in mode_map:
                mode = mode_map[auth_mode]
        elif hasattr(oracledb, 'SYSDBA'):
            mode_map = {
                'SYSDBA': oracledb.SYSDBA,
                'SYSOPER': oracledb.SYSOPER,
            }
            if auth_mode in mode_map:
                mode = mode_map[auth_mode]
        
        # Connect
        if mode:
            conn = oracledb.connect(user=username, password=password, dsn=dsn, mode=mode)
        else:
            conn = oracledb.connect(user=username, password=password, dsn=dsn)
        
        # Get database info
        cursor = conn.cursor()
        cursor.execute("SELECT banner FROM v$version WHERE ROWNUM = 1")
        version = cursor.fetchone()[0]
        
        cursor.execute("SELECT instance_name FROM v$instance")
        instance = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return True, f"Successfully authenticated to Oracle Database\nInstance: {instance}\nVersion: {version}"
        
    except oracledb.DatabaseError as e:
        error, = e.args
        if hasattr(error, 'code'):
            error_codes = {
                1017: "ORA-01017: Invalid username/password",
                12541: "ORA-12541: TNS: No listener",
                12543: "ORA-12543: TNS: Destination host unreachable",
                12514: "ORA-12514: TNS: Listener does not know of service",
                28000: "ORA-28000: Account is locked",
                28001: "ORA-28001: Password has expired",
            }
            msg = error_codes.get(error.code, str(error))
            return False, f"Oracle error: {msg}"
        return False, f"Oracle error: {error}"
    except Exception as e:
        return False, f"Error: {e}"

