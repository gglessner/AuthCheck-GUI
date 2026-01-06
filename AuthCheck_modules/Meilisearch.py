# Meilisearch Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Meilisearch (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "7700",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "7700"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "api_key", "type": "password", "label": "API Key (Master/Admin)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 443, Non-TLS: 7700. Master key in env/config."},
]


def authenticate(form_data):
    """Attempt to authenticate to Meilisearch."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '7700').strip()
    use_https = form_data.get('use_https', False)
    api_key = form_data.get('api_key', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        headers = {}
        if api_key:
            headers['Authorization'] = f"Bearer {api_key}"
        
        # Get version
        response = requests.get(f"{base_url}/version", headers=headers,
                               verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('pkgVersion', 'unknown')
            
            # Get indexes
            indexes_resp = requests.get(f"{base_url}/indexes", headers=headers,
                                       verify=verify_ssl, timeout=10)
            indexes = []
            if indexes_resp.status_code == 200:
                indexes_data = indexes_resp.json()
                indexes = [idx.get('uid') for idx in indexes_data.get('results', [])]
            
            # Get stats
            stats_resp = requests.get(f"{base_url}/stats", headers=headers,
                                     verify=verify_ssl, timeout=10)
            total_docs = 0
            if stats_resp.status_code == 200:
                stats = stats_resp.json()
                total_docs = sum(idx.get('numberOfDocuments', 0) 
                               for idx in stats.get('indexes', {}).values())
            
            return True, f"Successfully connected to Meilisearch {version}\nIndexes: {len(indexes)}, Documents: {total_docs}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API key"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, f"Meilisearch error: {e}"

