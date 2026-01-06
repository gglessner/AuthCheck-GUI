# ClickHouse Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "ClickHouse (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8123",
     "port_toggle": "use_ssl", "tls_port": "8443", "non_tls_port": "8123"},
    {"name": "username", "type": "text", "label": "Username", "default": "default"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "database", "type": "text", "label": "Database", "default": "default"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "HTTPS: 8443, HTTP: 8123, Native: 9000/9440. default / (empty)"},
]


def authenticate(form_data):
    """Attempt to authenticate to ClickHouse."""
    try:
        import clickhouse_connect
    except ImportError:
        try:
            import requests
            use_http = True
        except ImportError:
            return False, "clickhouse-connect or requests package not installed. Run: pip install clickhouse-connect"
        use_http = True
    else:
        use_http = False
    
    host = form_data.get('host', 'localhost').strip()
    port = form_data.get('port', '8123').strip()
    username = form_data.get('username', 'default').strip()
    password = form_data.get('password', '')
    database = form_data.get('database', 'default').strip()
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        if use_http:
            # Use HTTP interface
            import requests
            scheme = "https" if use_ssl else "http"
            base_url = f"{scheme}://{host}:{port}"
            
            params = {'user': username, 'password': password, 'database': database}
            
            # Get version
            response = requests.get(f"{base_url}/?query=SELECT%20version()",
                                   params={'user': username, 'password': password},
                                   timeout=10)
            
            if response.status_code == 200:
                version = response.text.strip()
                
                # Get database count
                db_resp = requests.get(f"{base_url}/?query=SELECT%20count()%20FROM%20system.databases",
                                      params={'user': username, 'password': password},
                                      timeout=10)
                db_count = db_resp.text.strip() if db_resp.status_code == 200 else 'unknown'
                
                return True, f"Successfully authenticated to ClickHouse {version}\nDatabases: {db_count}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:200]}"
        else:
            # Use native client
            client = clickhouse_connect.get_client(
                host=host,
                port=int(port),
                username=username,
                password=password,
                database=database,
                secure=use_ssl
            )
            
            # Get version
            version = client.server_version
            
            # Get database count
            result = client.query("SELECT count() FROM system.databases")
            db_count = result.result_rows[0][0]
            
            # Get table count
            result = client.query("SELECT count() FROM system.tables")
            table_count = result.result_rows[0][0]
            
            client.close()
            
            return True, f"Successfully authenticated to ClickHouse {version}\nDatabases: {db_count}\nTables: {table_count}"
        
    except Exception as e:
        return False, f"ClickHouse error: {e}"

