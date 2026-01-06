# Apache Samza Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Samza (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Job Coordinator Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "REST Port", "default": "9090",
     "port_toggle": "use_https", "tls_port": "9090", "non_tls_port": "9090"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "REST: 9090 (TLS/non-TLS same). Uses YARN/Kafka auth."},
]


def authenticate(form_data):
    """
    Attempt to connect to Apache Samza REST API.
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
        return False, "Job Coordinator Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "9090"
        base_url = f"{scheme}://{host}:{port_num}"
        
        # Get job status
        url = f"{base_url}/v1/jobs"
        response = requests.get(url, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            jobs = data if isinstance(data, list) else data.get('jobs', [])
            
            job_info = []
            for job in jobs[:5]:  # Show first 5 jobs
                name = job.get('jobName', 'unknown')
                status = job.get('status', 'unknown')
                job_info.append(f"{name}({status})")
            
            return True, f"Successfully connected to Apache Samza at {host}:{port_num}\nJobs: {', '.join(job_info) if job_info else 'None'}"
        elif response.status_code == 404:
            return False, "Samza REST API not found"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Samza error: {e}"

