# InfluxDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "InfluxDB (DB)"

form_fields = [
    {"name": "url", "type": "text", "label": "URL", "default": "http://localhost:8086"},
    {"name": "version", "type": "combo", "label": "InfluxDB Version",
     "options": ["2.x", "1.x"]},
    {"name": "token", "type": "password", "label": "API Token (2.x)"},
    {"name": "org", "type": "text", "label": "Organization (2.x)"},
    {"name": "username", "type": "text", "label": "Username (1.x)"},
    {"name": "password", "type": "password", "label": "Password (1.x)"},
    {"name": "database", "type": "text", "label": "Database (1.x)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "1.x: admin / admin, root / root. 2.x: token from setup"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to InfluxDB.
    """
    url = form_data.get('url', '').strip()
    version = form_data.get('version', '2.x')
    token = form_data.get('token', '').strip()
    org = form_data.get('org', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    database = form_data.get('database', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not url:
        return False, "URL is required"
    
    if version == "2.x":
        try:
            from influxdb_client import InfluxDBClient
        except ImportError:
            return False, "influxdb-client package not installed. Run: pip install influxdb-client"
        
        if not token:
            return False, "API Token is required for InfluxDB 2.x"
        
        try:
            client = InfluxDBClient(
                url=url,
                token=token,
                org=org if org else None,
                verify_ssl=verify_ssl,
                timeout=10000
            )
            
            # Check health
            health = client.health()
            
            if health.status == "pass":
                # Get org info if possible
                try:
                    orgs_api = client.organizations_api()
                    orgs = orgs_api.find_organizations()
                    org_names = [o.name for o in orgs]
                    client.close()
                    return True, f"Successfully authenticated to InfluxDB 2.x\nHealth: {health.status}\nOrganizations: {org_names}"
                except:
                    client.close()
                    return True, f"Successfully authenticated to InfluxDB 2.x\nHealth: {health.status}"
            else:
                client.close()
                return False, f"InfluxDB health check failed: {health.message}"
                
        except Exception as e:
            error_msg = str(e)
            if "unauthorized" in error_msg.lower() or "401" in error_msg:
                return False, "Authentication failed: Invalid token"
            return False, f"InfluxDB error: {e}"
    
    else:  # 1.x
        try:
            from influxdb import InfluxDBClient
        except ImportError:
            return False, "influxdb package not installed. Run: pip install influxdb"
        
        try:
            # Parse URL
            from urllib.parse import urlparse
            parsed = urlparse(url)
            host = parsed.hostname or 'localhost'
            port = parsed.port or 8086
            ssl = parsed.scheme == 'https'
            
            client = InfluxDBClient(
                host=host,
                port=port,
                username=username,
                password=password,
                database=database if database else None,
                ssl=ssl,
                verify_ssl=verify_ssl,
                timeout=10
            )
            
            # Test connection
            version_info = client.ping()
            databases = client.get_list_database()
            db_names = [db['name'] for db in databases]
            
            client.close()
            
            return True, f"Successfully authenticated to InfluxDB 1.x\nVersion: {version_info}\nDatabases: {db_names}"
            
        except Exception as e:
            error_msg = str(e)
            if "unauthorized" in error_msg.lower() or "401" in error_msg:
                return False, "Authentication failed: Invalid credentials"
            return False, f"InfluxDB error: {e}"

