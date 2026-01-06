# Pinecone Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Pinecone (DB)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "environment", "type": "text", "label": "Environment", "default": "us-east-1-aws"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API key from Pinecone Console. Vector database for AI/ML."},
]


def authenticate(form_data):
    """Attempt to authenticate to Pinecone."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    api_key = form_data.get('api_key', '').strip()
    environment = form_data.get('environment', '').strip()
    
    if not api_key:
        return False, "API Key is required"
    
    try:
        headers = {
            'Api-Key': api_key,
            'Accept': 'application/json'
        }
        
        # List indexes
        response = requests.get(
            "https://api.pinecone.io/indexes",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            indexes = data.get('indexes', [])
            index_count = len(indexes)
            index_names = [idx.get('name', 'unknown') for idx in indexes[:5]]
            
            return True, f"Successfully authenticated to Pinecone\nEnvironment: {environment}\nIndexes: {index_count}\nSample: {', '.join(index_names) if index_names else 'none'}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API key"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Pinecone error: {e}"

