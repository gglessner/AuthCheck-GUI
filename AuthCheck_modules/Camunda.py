# Camunda BPM Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Camunda BPM (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "context_path", "type": "text", "label": "Context Path", "default": "/engine-rest"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username", "default": "demo"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8443, Non-TLS: 8080. demo / demo, admin / admin"},
]


def authenticate(form_data):
    """Attempt to authenticate to Camunda BPM."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8080').strip()
    context_path = form_data.get('context_path', '/engine-rest').strip()
    use_https = form_data.get('use_https', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{port}{context_path}"
        
        auth = HTTPBasicAuth(username, password) if username else None
        
        # Get engine info
        response = requests.get(f"{base_url}/engine", auth=auth,
                               verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            engines = response.json()
            engine_name = engines[0].get('name', 'default') if engines else 'unknown'
            
            # Get process definitions count
            pd_resp = requests.get(f"{base_url}/process-definition/count", auth=auth,
                                  verify=verify_ssl, timeout=10)
            process_defs = pd_resp.json().get('count', 0) if pd_resp.status_code == 200 else 0
            
            # Get running process instances
            pi_resp = requests.get(f"{base_url}/process-instance/count", auth=auth,
                                  verify=verify_ssl, timeout=10)
            instances = pi_resp.json().get('count', 0) if pi_resp.status_code == 200 else 0
            
            # Get deployments
            deploy_resp = requests.get(f"{base_url}/deployment/count", auth=auth,
                                      verify=verify_ssl, timeout=10)
            deployments = deploy_resp.json().get('count', 0) if deploy_resp.status_code == 200 else 0
            
            return True, f"Successfully authenticated to Camunda engine '{engine_name}'\nProcess Definitions: {process_defs}\nRunning Instances: {instances}\nDeployments: {deployments}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, f"Camunda error: {e}"

