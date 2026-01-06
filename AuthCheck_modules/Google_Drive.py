# Google Drive Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Google Drive (Collaboration)"

form_fields = [
    {"name": "service_account_file", "type": "file", "label": "Service Account JSON", "file_filter": "JSON Files (*.json)"},
    {"name": "access_token", "type": "password", "label": "Access Token (Alternative)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Service account from Google Cloud Console. Requires Drive API enabled."},
]


def authenticate(form_data):
    """Attempt to authenticate to Google Drive."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    service_account_file = form_data.get('service_account_file', '').strip()
    access_token = form_data.get('access_token', '').strip()
    
    try:
        if access_token:
            token = access_token
        elif service_account_file:
            try:
                from google.oauth2 import service_account
                from google.auth.transport.requests import Request
            except ImportError:
                return False, "google-auth package not installed. Run: pip install google-auth"
            
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            credentials.refresh(Request())
            token = credentials.token
        else:
            return False, "Service Account JSON or Access Token required"
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get about info
        about_resp = requests.get(
            "https://www.googleapis.com/drive/v3/about?fields=user,storageQuota",
            headers=headers,
            timeout=15
        )
        
        if about_resp.status_code == 200:
            about = about_resp.json()
            user = about.get('user', {})
            email = user.get('emailAddress', 'unknown')
            display_name = user.get('displayName', 'unknown')
            
            quota = about.get('storageQuota', {})
            usage = int(quota.get('usage', 0)) / (1024**3)  # Convert to GB
            limit = quota.get('limit')
            limit_str = f"{int(limit) / (1024**3):.1f} GB" if limit else "Unlimited"
            
            # Get recent files count
            files_resp = requests.get(
                "https://www.googleapis.com/drive/v3/files?pageSize=100",
                headers=headers,
                timeout=10
            )
            file_count = 0
            if files_resp.status_code == 200:
                file_count = len(files_resp.json().get('files', []))
            
            return True, f"Successfully authenticated to Google Drive\nUser: {display_name} ({email})\nUsage: {usage:.2f} GB / {limit_str}\nRecent Files: {file_count}"
        elif about_resp.status_code == 401:
            return False, "Authentication failed: Invalid or expired token"
        else:
            return False, f"HTTP {about_resp.status_code}: {about_resp.text[:200]}"
            
    except Exception as e:
        return False, f"Google Drive error: {e}"

