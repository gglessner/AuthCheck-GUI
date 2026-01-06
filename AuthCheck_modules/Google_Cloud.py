# Google Cloud Platform Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Google Cloud Platform (Cloud)"

form_fields = [
    {"name": "credentials_file", "type": "file", "label": "Service Account JSON", "filter": "JSON Files (*.json);;All Files (*)"},
    {"name": "project_id", "type": "text", "label": "Project ID (Optional)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Service Account JSON from IAM > Service Accounts > Keys. Or use GOOGLE_APPLICATION_CREDENTIALS env var."},
]


def authenticate(form_data):
    """Attempt to authenticate to Google Cloud Platform."""
    try:
        from google.oauth2 import service_account
        from google.cloud import resourcemanager_v3
    except ImportError:
        return False, "google-cloud packages not installed. Run: pip install google-cloud-resource-manager google-auth"
    
    credentials_file = form_data.get('credentials_file', '').strip()
    project_id = form_data.get('project_id', '').strip()
    
    try:
        if credentials_file:
            credentials = service_account.Credentials.from_service_account_file(credentials_file)
        else:
            # Try default credentials
            import google.auth
            credentials, default_project = google.auth.default()
            if not project_id:
                project_id = default_project
        
        # Get service account info
        sa_email = 'unknown'
        if hasattr(credentials, 'service_account_email'):
            sa_email = credentials.service_account_email
        
        # List projects the service account can access
        client = resourcemanager_v3.ProjectsClient(credentials=credentials)
        
        project_count = 0
        project_names = []
        try:
            request = resourcemanager_v3.SearchProjectsRequest()
            for project in client.search_projects(request=request):
                project_count += 1
                if project_count <= 5:
                    project_names.append(project.display_name or project.project_id)
        except Exception:
            pass
        
        return True, f"Successfully authenticated to Google Cloud\nService Account: {sa_email}\nAccessible Projects: {project_count}\nProjects: {', '.join(project_names)}{'...' if project_count > 5 else ''}"
        
    except Exception as e:
        return False, f"GCP error: {e}"

