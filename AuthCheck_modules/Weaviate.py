# Weaviate Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Weaviate (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Weaviate Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "8080",
     "port_toggle": "use_ssl", "tls_port": "443", "non_tls_port": "8080"},
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 443, Non-TLS: 8080. API key for Weaviate Cloud."},
]


def authenticate(form_data):
    """Attempt to authenticate to Weaviate."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8080').strip()
    api_key = form_data.get('api_key', '').strip()
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "Weaviate Host is required"
    
    try:
        scheme = "https" if use_ssl else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        headers = {'Accept': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        # Get meta info
        response = requests.get(
            f"{base_url}/v1/meta",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            meta = response.json()
            version = meta.get('version', 'unknown')
            
            # Get schema (classes)
            schema_resp = requests.get(
                f"{base_url}/v1/schema",
                headers=headers,
                timeout=10
            )
            class_count = 0
            class_names = []
            if schema_resp.status_code == 200:
                classes = schema_resp.json().get('classes', [])
                class_count = len(classes)
                class_names = [c.get('class', 'unknown') for c in classes[:5]]
            
            return True, f"Successfully authenticated to Weaviate\nHost: {host}:{port}\nVersion: {version}\nClasses: {class_count}\nSample: {', '.join(class_names) if class_names else 'none'}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API key"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Weaviate error: {e}"

