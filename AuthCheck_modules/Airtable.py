# Airtable Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Airtable (Collaboration)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "Personal Access Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "PAT from airtable.com/create/tokens. Legacy API keys deprecated."},
]


def authenticate(form_data):
    """Attempt to authenticate to Airtable."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    api_key = form_data.get('api_key', '').strip()
    
    if not api_key:
        return False, "Personal Access Token is required"
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Get current user
        response = requests.get("https://api.airtable.com/v0/meta/whoami",
                               headers=headers, timeout=15)
        
        if response.status_code == 200:
            user = response.json()
            user_id = user.get('id', 'unknown')
            
            # List bases
            bases_resp = requests.get("https://api.airtable.com/v0/meta/bases",
                                     headers=headers, timeout=10)
            base_count = 0
            base_names = []
            if bases_resp.status_code == 200:
                bases = bases_resp.json().get('bases', [])
                base_count = len(bases)
                base_names = [b['name'] for b in bases[:3]]
            
            return True, f"Successfully authenticated to Airtable\nUser ID: {user_id}\nBases: {base_count}\nSample: {', '.join(base_names) if base_names else 'none'}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Airtable error: {e}"

