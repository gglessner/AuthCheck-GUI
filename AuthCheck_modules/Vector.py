# Vector Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Vector (Logging)"

form_fields = [
    {"name": "host", "type": "text", "label": "Vector Host"},
    {"name": "port", "type": "text", "label": "API Port", "default": "8686",
     "port_toggle": "use_ssl", "tls_port": "8686", "non_tls_port": "8686"},
    {"name": "api_key", "type": "password", "label": "API Key (if configured)"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API: 8686 (TLS/non-TLS same). Enable [api] in vector.toml."},
]


def authenticate(form_data):
    """Attempt to authenticate to Vector."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8686').strip()
    api_key = form_data.get('api_key', '').strip()
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "Vector Host is required"
    
    try:
        scheme = "https" if use_ssl else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        headers = {'Content-Type': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        # GraphQL query for health and version
        query = """
        {
            health
            meta {
                version
            }
            sources {
                edges {
                    node {
                        componentId
                        componentType
                    }
                }
            }
            transforms {
                edges {
                    node {
                        componentId
                    }
                }
            }
            sinks {
                edges {
                    node {
                        componentId
                    }
                }
            }
        }
        """
        
        response = requests.post(
            f"{base_url}/graphql",
            headers=headers,
            json={'query': query},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            health = data.get('health', False)
            version = data.get('meta', {}).get('version', 'unknown')
            sources = len(data.get('sources', {}).get('edges', []))
            transforms = len(data.get('transforms', {}).get('edges', []))
            sinks = len(data.get('sinks', {}).get('edges', []))
            
            status = "Healthy" if health else "Unhealthy"
            
            return True, f"Successfully authenticated to Vector\nHost: {host}:{port}\nVersion: {version}\nStatus: {status}\nSources: {sources}, Transforms: {transforms}, Sinks: {sinks}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API key"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Vector error: {e}"

