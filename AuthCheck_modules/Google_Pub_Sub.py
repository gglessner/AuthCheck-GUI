# Google Cloud Pub/Sub Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Google Cloud Pub/Sub (Cloud)"

form_fields = [
    {"name": "credentials_file", "type": "file", "label": "Service Account JSON", "filter": "JSON Files (*.json);;All Files (*)"},
    {"name": "project_id", "type": "text", "label": "Project ID"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Service Account JSON from GCP Console. Requires pubsub.topics.list permission."},
]


def authenticate(form_data):
    """Attempt to authenticate to Google Cloud Pub/Sub."""
    try:
        from google.cloud import pubsub_v1
        from google.oauth2 import service_account
    except ImportError:
        return False, "google-cloud-pubsub package not installed. Run: pip install google-cloud-pubsub"
    
    credentials_file = form_data.get('credentials_file', '').strip()
    project_id = form_data.get('project_id', '').strip()
    
    if not project_id:
        return False, "Project ID is required"
    
    try:
        if credentials_file:
            credentials = service_account.Credentials.from_service_account_file(credentials_file)
            publisher = pubsub_v1.PublisherClient(credentials=credentials)
            subscriber = pubsub_v1.SubscriberClient(credentials=credentials)
        else:
            publisher = pubsub_v1.PublisherClient()
            subscriber = pubsub_v1.SubscriberClient()
        
        project_path = f"projects/{project_id}"
        
        # List topics
        topics = list(publisher.list_topics(request={"project": project_path}))
        topic_names = [t.name.split('/')[-1] for t in topics[:5]]
        
        # List subscriptions
        subscriptions = list(subscriber.list_subscriptions(request={"project": project_path}))
        
        return True, f"Successfully authenticated to Google Cloud Pub/Sub\nProject: {project_id}\nTopics: {len(topics)}\nSubscriptions: {len(subscriptions)}\nSample Topics: {', '.join(topic_names) if topic_names else 'none'}"
        
    except Exception as e:
        return False, f"Google Pub/Sub error: {e}"

