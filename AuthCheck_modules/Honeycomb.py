# Honeycomb Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Honeycomb (Monitoring)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API key from Team Settings > API Keys. Configuration key starts with hca..."},
]


def authenticate(form_data):
    """Attempt to authenticate to Honeycomb."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    api_key = form_data.get('api_key', '').strip()
    
    if not api_key:
        return False, "API Key is required"
    
    try:
        headers = {
            'X-Honeycomb-Team': api_key,
            'Accept': 'application/json'
        }
        
        # Get auth info
        response = requests.get(
            "https://api.honeycomb.io/1/auth",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            team_name = data.get('team', {}).get('name', 'unknown')
            team_slug = data.get('team', {}).get('slug', 'unknown')
            
            # Get datasets
            datasets_resp = requests.get(
                "https://api.honeycomb.io/1/datasets",
                headers=headers,
                timeout=10
            )
            dataset_count = 0
            dataset_names = []
            if datasets_resp.status_code == 200:
                datasets = datasets_resp.json()
                dataset_count = len(datasets)
                dataset_names = [d.get('name', 'unknown') for d in datasets[:5]]
            
            return True, f"Successfully authenticated to Honeycomb\nTeam: {team_name} ({team_slug})\nDatasets: {dataset_count}\nSample: {', '.join(dataset_names) if dataset_names else 'none'}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API key"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Honeycomb error: {e}"

