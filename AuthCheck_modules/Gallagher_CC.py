# Gallagher Command Centre Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Gallagher Command Centre (Access Control)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.100"},
    {"name": "port", "type": "text", "label": "Port", "default": "8904"},
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API key auth. REST API: 8904"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Gallagher Command Centre.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8904').strip()
    api_key = form_data.get('api_key', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not api_key:
        return False, "API Key is required"
    
    base_url = f"https://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # Gallagher REST API
        headers = {
            "Authorization": f"GGL-API-KEY {api_key}",
            "Accept": "application/json"
        }
        
        api_url = f"{base_url}/api"
        response = session.get(api_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            version = data.get("version", "unknown")
            
            # Get features
            features = data.get("features", {})
            
            return True, f"Successfully authenticated to Gallagher CC at {host}\nAPI Version: {version}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API key"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Gallagher error: {e}"

