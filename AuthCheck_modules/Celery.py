# Celery (Flower) Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Celery (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Flower Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Flower Port", "default": "5555",
     "port_toggle": "use_https", "tls_port": "5555", "non_tls_port": "5555"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Flower: 5555 (TLS/non-TLS same). Uses broker auth."},
]


def authenticate(form_data):
    """Attempt to authenticate to Celery Flower dashboard."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '5555').strip()
    use_https = form_data.get('use_https', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Flower Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{port}/api"
        
        auth = HTTPBasicAuth(username, password) if username else None
        
        # Get workers
        response = requests.get(f"{base_url}/workers", auth=auth,
                               verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            workers = response.json()
            worker_names = list(workers.keys())
            
            # Get tasks
            tasks_resp = requests.get(f"{base_url}/tasks", auth=auth,
                                     verify=verify_ssl, timeout=10)
            tasks = {}
            if tasks_resp.status_code == 200:
                tasks = tasks_resp.json()
            
            active = sum(1 for w in workers.values() if w.get('status'))
            
            return True, f"Successfully connected to Celery Flower at {host}:{port}\nWorkers: {len(worker_names)} ({active} active)\nRegistered Tasks: {len(tasks)}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, f"Flower error: {e}"

