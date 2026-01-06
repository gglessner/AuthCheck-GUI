# Google Cloud Spanner Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Google Cloud Spanner (Cloud)"

form_fields = [
    {"name": "project_id", "type": "text", "label": "Project ID"},
    {"name": "instance_id", "type": "text", "label": "Instance ID"},
    {"name": "database_id", "type": "text", "label": "Database ID"},
    {"name": "service_account_file", "type": "file", "label": "Service Account JSON", "file_filter": "JSON Files (*.json)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Service account from Google Cloud Console. Globally distributed SQL."},
]


def authenticate(form_data):
    """Attempt to authenticate to Google Cloud Spanner."""
    try:
        from google.cloud import spanner
        from google.oauth2 import service_account
    except ImportError:
        return False, "google-cloud-spanner package not installed. Run: pip install google-cloud-spanner"
    
    project_id = form_data.get('project_id', '').strip()
    instance_id = form_data.get('instance_id', '').strip()
    database_id = form_data.get('database_id', '').strip()
    service_account_file = form_data.get('service_account_file', '').strip()
    
    if not project_id:
        return False, "Project ID is required"
    if not instance_id:
        return False, "Instance ID is required"
    
    try:
        if service_account_file:
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file
            )
            client = spanner.Client(project=project_id, credentials=credentials)
        else:
            client = spanner.Client(project=project_id)
        
        # Get instance
        instance = client.instance(instance_id)
        
        # Check if instance exists
        if instance.exists():
            instance.reload()
            config = instance.configuration_name
            node_count = instance.node_count
            
            # Get databases
            databases = list(instance.list_databases())
            db_names = [db.name.split('/')[-1] for db in databases[:5]]
            
            if database_id:
                database = instance.database(database_id)
                if database.exists():
                    return True, f"Successfully authenticated to Cloud Spanner\nProject: {project_id}\nInstance: {instance_id}\nConfig: {config}\nNodes: {node_count}\nDatabase: {database_id} (connected)"
            
            return True, f"Successfully authenticated to Cloud Spanner\nProject: {project_id}\nInstance: {instance_id}\nConfig: {config}\nNodes: {node_count}\nDatabases: {len(databases)}"
        else:
            return False, f"Instance {instance_id} not found"
            
    except Exception as e:
        return False, f"Cloud Spanner error: {e}"

