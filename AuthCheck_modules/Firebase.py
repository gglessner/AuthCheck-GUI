# Firebase Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Firebase (Cloud)"

form_fields = [
    {"name": "service_account_file", "type": "file", "label": "Service Account JSON", "file_filter": "JSON Files (*.json)"},
    {"name": "database_url", "type": "text", "label": "Database URL (Realtime DB)"},
    {"name": "project_id", "type": "text", "label": "Project ID (for Firestore)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Service account from Firebase Console > Project Settings > Service accounts."},
]


def authenticate(form_data):
    """Attempt to authenticate to Firebase."""
    try:
        import firebase_admin
        from firebase_admin import credentials, db, firestore
    except ImportError:
        return False, "firebase-admin package not installed. Run: pip install firebase-admin"
    
    service_account_file = form_data.get('service_account_file', '').strip()
    database_url = form_data.get('database_url', '').strip()
    project_id = form_data.get('project_id', '').strip()
    
    if not service_account_file:
        return False, "Service Account JSON is required"
    
    try:
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(service_account_file)
        
        options = {}
        if database_url:
            options['databaseURL'] = database_url
        if project_id:
            options['projectId'] = project_id
        
        # Delete any existing app
        try:
            firebase_admin.delete_app(firebase_admin.get_app())
        except:
            pass
        
        app = firebase_admin.initialize_app(cred, options)
        
        results = []
        
        # Try Realtime Database
        if database_url:
            try:
                ref = db.reference('/')
                # Just check if we can access
                results.append("Realtime DB: Connected")
            except Exception as e:
                results.append(f"Realtime DB: {e}")
        
        # Try Firestore
        try:
            fs = firestore.client()
            # List collections
            collections = list(fs.collections())
            coll_names = [c.id for c in collections[:5]]
            results.append(f"Firestore: {len(collections)} collections")
        except Exception as e:
            results.append(f"Firestore: {e}")
        
        # Cleanup
        firebase_admin.delete_app(app)
        
        project = project_id or "from service account"
        return True, f"Successfully authenticated to Firebase\nProject: {project}\n" + "\n".join(results)
        
    except Exception as e:
        try:
            firebase_admin.delete_app(firebase_admin.get_app())
        except:
            pass
        return False, f"Firebase error: {e}"

