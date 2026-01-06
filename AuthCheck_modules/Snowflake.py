# Snowflake Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Snowflake (DB)"

form_fields = [
    {"name": "account", "type": "text", "label": "Account Identifier"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "warehouse", "type": "text", "label": "Warehouse"},
    {"name": "database", "type": "text", "label": "Database"},
    {"name": "schema", "type": "text", "label": "Schema", "default": "PUBLIC"},
    {"name": "role", "type": "text", "label": "Role"},
    {"name": "auth_type", "type": "combo", "label": "Authentication", "options": ["Password", "SSO (Browser)", "Key Pair"], "default": "Password"},
    {"name": "private_key_file", "type": "file", "label": "Private Key File", "filter": "Key Files (*.pem *.p8);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Account format: orgname-accountname or locator.region.cloud"},
]


def authenticate(form_data):
    """Attempt to authenticate to Snowflake."""
    try:
        import snowflake.connector
    except ImportError:
        return False, "snowflake-connector-python package not installed. Run: pip install snowflake-connector-python"
    
    account = form_data.get('account', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    warehouse = form_data.get('warehouse', '').strip()
    database = form_data.get('database', '').strip()
    schema = form_data.get('schema', 'PUBLIC').strip()
    role = form_data.get('role', '').strip()
    auth_type = form_data.get('auth_type', 'Password')
    private_key_file = form_data.get('private_key_file', '').strip()
    
    if not account:
        return False, "Account Identifier is required"
    if not username:
        return False, "Username is required"
    
    try:
        conn_params = {
            'account': account,
            'user': username,
        }
        
        if auth_type == "Password":
            conn_params['password'] = password
        elif auth_type == "SSO (Browser)":
            conn_params['authenticator'] = 'externalbrowser'
        elif auth_type == "Key Pair" and private_key_file:
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import serialization
            with open(private_key_file, 'rb') as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=password.encode() if password else None,
                    backend=default_backend()
                )
            conn_params['private_key'] = private_key
        
        if warehouse:
            conn_params['warehouse'] = warehouse
        if database:
            conn_params['database'] = database
        if schema:
            conn_params['schema'] = schema
        if role:
            conn_params['role'] = role
        
        conn = snowflake.connector.connect(**conn_params)
        cursor = conn.cursor()
        
        # Get current context
        cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE()")
        row = cursor.fetchone()
        current_user = row[0]
        current_role = row[1]
        current_wh = row[2]
        current_db = row[3]
        
        # Get version
        cursor.execute("SELECT CURRENT_VERSION()")
        version = cursor.fetchone()[0]
        
        conn.close()
        return True, f"Successfully authenticated to Snowflake {version}\nUser: {current_user}\nRole: {current_role}\nWarehouse: {current_wh}\nDatabase: {current_db}"
        
    except Exception as e:
        return False, f"Snowflake error: {e}"

