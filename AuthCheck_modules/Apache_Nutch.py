# Apache Nutch Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Nutch (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8081",
     "port_toggle": "use_https", "tls_port": "8081", "non_tls_port": "8081"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 8081 (TLS/non-TLS same). Crawler, no native auth."},
]


def authenticate(form_data):
    """
    Attempt to connect to Apache Nutch REST API.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "8081"
        base_url = f"{scheme}://{host}:{port_num}"
        
        # Get admin info
        url = f"{base_url}/admin"
        response = requests.get(url, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            # Get jobs
            jobs_url = f"{base_url}/job"
            jobs_response = requests.get(jobs_url, verify=verify_ssl, timeout=10)
            jobs = []
            if jobs_response.status_code == 200:
                jobs_data = jobs_response.json()
                jobs = jobs_data if isinstance(jobs_data, list) else []
            
            # Get configs
            config_url = f"{base_url}/config"
            config_response = requests.get(config_url, verify=verify_ssl, timeout=10)
            configs = []
            if config_response.status_code == 200:
                configs_data = config_response.json()
                configs = configs_data if isinstance(configs_data, list) else []
            
            return True, f"Successfully connected to Apache Nutch at {host}:{port_num}\nJobs: {len(jobs)}, Configs: {len(configs)}"
        elif response.status_code == 404:
            return False, "Nutch REST API not found (ensure REST server is running)"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Nutch error: {e}"

