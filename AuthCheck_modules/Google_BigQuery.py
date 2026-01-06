# Google BigQuery Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Google BigQuery (Cloud)"

form_fields = [
    {"name": "credentials_file", "type": "file", "label": "Service Account JSON", "filter": "JSON Files (*.json);;All Files (*)"},
    {"name": "project_id", "type": "text", "label": "Project ID"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Service Account JSON from GCP Console > IAM > Service Accounts > Keys. Requires BigQuery permissions."},
]


def authenticate(form_data):
    """Attempt to authenticate to Google BigQuery."""
    try:
        from google.cloud import bigquery
        from google.oauth2 import service_account
    except ImportError:
        return False, "google-cloud-bigquery package not installed. Run: pip install google-cloud-bigquery"
    
    credentials_file = form_data.get('credentials_file', '').strip()
    project_id = form_data.get('project_id', '').strip()
    
    try:
        if credentials_file:
            credentials = service_account.Credentials.from_service_account_file(credentials_file)
            if project_id:
                client = bigquery.Client(credentials=credentials, project=project_id)
            else:
                client = bigquery.Client(credentials=credentials)
        else:
            # Use default credentials
            if project_id:
                client = bigquery.Client(project=project_id)
            else:
                client = bigquery.Client()
        
        # List datasets
        datasets = list(client.list_datasets())
        dataset_names = [ds.dataset_id for ds in datasets[:5]]
        
        project = client.project
        
        return True, f"Successfully authenticated to Google BigQuery\nProject: {project}\nDatasets: {len(datasets)}\nSample: {', '.join(dataset_names) if dataset_names else 'none'}"
        
    except Exception as e:
        return False, f"BigQuery error: {e}"

