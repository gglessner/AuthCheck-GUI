# Google Cloud Storage Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Google Cloud Storage (Cloud)"

form_fields = [
    {"name": "credentials_file", "type": "file", "label": "Service Account JSON", "filter": "JSON Files (*.json);;All Files (*)"},
    {"name": "project_id", "type": "text", "label": "Project ID"},
    {"name": "bucket", "type": "text", "label": "Test Bucket (Optional)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Service Account JSON from GCP Console. Requires storage.buckets.list permission."},
]


def authenticate(form_data):
    """Attempt to authenticate to Google Cloud Storage."""
    try:
        from google.cloud import storage
        from google.oauth2 import service_account
    except ImportError:
        return False, "google-cloud-storage package not installed. Run: pip install google-cloud-storage"
    
    credentials_file = form_data.get('credentials_file', '').strip()
    project_id = form_data.get('project_id', '').strip()
    bucket_name = form_data.get('bucket', '').strip()
    
    try:
        if credentials_file:
            credentials = service_account.Credentials.from_service_account_file(credentials_file)
            client = storage.Client(credentials=credentials, project=project_id if project_id else None)
        else:
            client = storage.Client(project=project_id if project_id else None)
        
        if bucket_name:
            # Test specific bucket
            bucket = client.get_bucket(bucket_name)
            return True, f"Successfully authenticated to Google Cloud Storage\nBucket: {bucket_name}\nLocation: {bucket.location}\nStorage Class: {bucket.storage_class}"
        else:
            # List buckets
            buckets = list(client.list_buckets())
            bucket_names = [b.name for b in buckets[:5]]
            
            return True, f"Successfully authenticated to Google Cloud Storage\nProject: {client.project}\nBuckets: {len(buckets)}\nSample: {', '.join(bucket_names) if bucket_names else 'none'}"
        
    except Exception as e:
        return False, f"Google Cloud Storage error: {e}"

