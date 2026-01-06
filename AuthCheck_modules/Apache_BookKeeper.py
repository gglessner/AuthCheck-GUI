# Apache BookKeeper Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache BookKeeper (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Bookie Host", "default": "localhost"},
    {"name": "http_port", "type": "text", "label": "HTTP Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "bookie_port", "type": "text", "label": "Bookie Port", "default": "3181"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "HTTP TLS: 8443, Non-TLS: 8080. Bookie: 3181. admin / admin"},
]


def authenticate(form_data):
    """
    Attempt to connect to Apache BookKeeper bookie.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    http_port = form_data.get('http_port', '').strip()
    use_https = form_data.get('use_https', False)
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Bookie Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = http_port if http_port else "8080"
        base_url = f"{scheme}://{host}:{port_num}/api/v1"
        
        # Get bookie state
        url = f"{base_url}/bookie/state"
        response = requests.get(url, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            running = data.get('running', False)
            readonly = data.get('readOnly', False)
            available = data.get('availableForHighPriorityWrites', False)
            
            # Get bookie info
            info_url = f"{base_url}/bookie/info"
            info_response = requests.get(info_url, verify=verify_ssl, timeout=10)
            free_space = 'unknown'
            if info_response.status_code == 200:
                info_data = info_response.json()
                free_space = info_data.get('freeSpace', 'unknown')
            
            state = "running" if running else "stopped"
            mode = "read-only" if readonly else "read-write"
            
            return True, f"Successfully connected to Apache BookKeeper at {host}:{port_num}\nState: {state}, Mode: {mode}\nFree Space: {free_space}"
        elif response.status_code == 404:
            return False, "BookKeeper HTTP service not found (ensure httpServerEnabled=true)"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"BookKeeper error: {e}"

