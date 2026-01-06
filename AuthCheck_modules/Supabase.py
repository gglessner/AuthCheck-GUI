# Supabase Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Supabase (Cloud)"

form_fields = [
    {"name": "project_url", "type": "text", "label": "Project URL"},
    {"name": "api_key", "type": "password", "label": "API Key (anon or service_role)"},
    {"name": "db_host", "type": "text", "label": "Database Host (Direct)"},
    {"name": "db_password", "type": "password", "label": "Database Password"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API key from Project Settings > API. PostgreSQL-based BaaS."},
]


def authenticate(form_data):
    """Attempt to authenticate to Supabase."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    project_url = form_data.get('project_url', '').strip()
    api_key = form_data.get('api_key', '').strip()
    db_host = form_data.get('db_host', '').strip()
    db_password = form_data.get('db_password', '')
    
    if not project_url and not db_host:
        return False, "Project URL or Database Host is required"
    
    try:
        # Try REST API first
        if project_url and api_key:
            if not project_url.startswith('http'):
                project_url = f"https://{project_url}"
            project_url = project_url.rstrip('/')
            
            headers = {
                'apikey': api_key,
                'Authorization': f'Bearer {api_key}'
            }
            
            # Health check
            response = requests.get(
                f"{project_url}/rest/v1/",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                # Get table list by querying pg_catalog
                tables_resp = requests.get(
                    f"{project_url}/rest/v1/",
                    headers={**headers, 'Prefer': 'count=exact'},
                    timeout=10
                )
                
                # Determine key type
                key_type = "service_role" if len(api_key) > 100 else "anon"
                
                return True, f"Successfully authenticated to Supabase\nProject: {project_url}\nKey Type: {key_type}\nAPI: Connected"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid API key"
        
        # Try direct PostgreSQL connection
        if db_host and db_password:
            try:
                import psycopg2
            except ImportError:
                return False, "psycopg2 package not installed for direct DB connection"
            
            conn = psycopg2.connect(
                host=db_host,
                port=5432,
                user='postgres',
                password=db_password,
                dbname='postgres',
                sslmode='require',
                connect_timeout=10
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            
            cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
            databases = [row[0] for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            return True, f"Successfully authenticated to Supabase (PostgreSQL)\nHost: {db_host}\nVersion: {version[:50]}...\nDatabases: {len(databases)}"
        
        return False, "Could not authenticate with provided credentials"
        
    except Exception as e:
        return False, f"Supabase error: {e}"

