# Apache SkyWalking Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache SkyWalking (Monitoring)"

form_fields = [
    {"name": "host", "type": "text", "label": "SkyWalking OAP Host"},
    {"name": "port", "type": "text", "label": "UI/GraphQL Port", "default": "12800",
     "port_toggle": "use_ssl", "tls_port": "12801", "non_tls_port": "12800"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "UI: 8080, gRPC: 11800, REST: 12800/12801. Auth per config."},
]


def authenticate(form_data):
    """Attempt to authenticate to Apache SkyWalking."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '12800').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "SkyWalking OAP Host is required"
    
    try:
        scheme = "https" if use_ssl else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        headers = {'Content-Type': 'application/json'}
        auth = None
        if username:
            auth = (username, password)
        
        # GraphQL query for services
        query = """
        {
            getAllServices(duration: {start: "2024-01-01", end: "2030-01-01", step: DAY}) {
                key: id
                label: name
            }
        }
        """
        
        response = requests.post(
            f"{base_url}/graphql",
            json={'query': query},
            headers=headers,
            auth=auth,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if 'errors' in data:
                # Try simpler version info query
                version_query = '{ version }'
                version_resp = requests.post(
                    f"{base_url}/graphql",
                    json={'query': version_query},
                    headers=headers,
                    auth=auth,
                    timeout=10
                )
                if version_resp.status_code == 200:
                    version_data = version_resp.json()
                    version = version_data.get('data', {}).get('version', 'unknown')
                    return True, f"Successfully connected to Apache SkyWalking\nHost: {host}:{port}\nVersion: {version}"
            
            services = data.get('data', {}).get('getAllServices', [])
            service_count = len(services)
            service_names = [s.get('label', 'unknown') for s in services[:5]]
            
            return True, f"Successfully connected to Apache SkyWalking\nHost: {host}:{port}\nServices: {service_count}\nSample: {', '.join(service_names) if service_names else 'none'}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"SkyWalking error: {e}"

