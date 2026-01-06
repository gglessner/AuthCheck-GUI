# LogRhythm Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "LogRhythm (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "LogRhythm Host"},
    {"name": "port", "type": "text", "label": "API Port", "default": "8501"},
    {"name": "api_token", "type": "password", "label": "API Token"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API token from Admin Console > API Keys. Default port 8501."},
]


def authenticate(form_data):
    """Attempt to authenticate to LogRhythm."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8501').strip()
    api_token = form_data.get('api_token', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "LogRhythm Host is required"
    if not api_token:
        return False, "API Token is required"
    
    try:
        base_url = f"https://{host}:{port}"
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        # Get entities (hosts)
        response = requests.get(
            f"{base_url}/lr-admin-api/entities",
            headers=headers,
            verify=verify_ssl,
            timeout=15
        )
        
        if response.status_code == 200:
            entities = response.json()
            entity_count = len(entities) if isinstance(entities, list) else 0
            
            # Get log sources
            logs_resp = requests.get(
                f"{base_url}/lr-admin-api/logsources",
                headers=headers,
                verify=verify_ssl,
                timeout=10
            )
            log_source_count = 0
            if logs_resp.status_code == 200:
                log_sources = logs_resp.json()
                log_source_count = len(log_sources) if isinstance(log_sources, list) else 0
            
            return True, f"Successfully authenticated to LogRhythm\nHost: {host}\nEntities: {entity_count}\nLog Sources: {log_source_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"LogRhythm error: {e}"

