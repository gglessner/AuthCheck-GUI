# Spinnaker Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Spinnaker (CI/CD)"

form_fields = [
    {"name": "gate_url", "type": "text", "label": "Gate URL"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "token", "type": "password", "label": "Bearer Token (Alternative)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Gate API default port 8084. Auth via LDAP, OAuth, or x509."},
]


def authenticate(form_data):
    """Attempt to authenticate to Spinnaker."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    gate_url = form_data.get('gate_url', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    token = form_data.get('token', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not gate_url:
        return False, "Gate URL is required"
    
    if not gate_url.startswith('http'):
        gate_url = f"https://{gate_url}"
    gate_url = gate_url.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        if token:
            session.headers['Authorization'] = f'Bearer {token}'
        elif username:
            session.auth = (username, password)
        
        # Get applications
        response = session.get(
            f"{gate_url}/applications",
            timeout=15
        )
        
        if response.status_code == 200:
            apps = response.json()
            app_count = len(apps)
            app_names = [a.get('name', 'unknown') for a in apps[:5]]
            
            # Get pipelines count
            pipeline_count = 0
            for app in apps[:10]:
                app_name = app.get('name')
                if app_name:
                    pipe_resp = session.get(
                        f"{gate_url}/applications/{app_name}/pipelineConfigs",
                        timeout=5
                    )
                    if pipe_resp.status_code == 200:
                        pipeline_count += len(pipe_resp.json())
            
            return True, f"Successfully authenticated to Spinnaker\nGate: {gate_url}\nApplications: {app_count}\nPipelines (sampled): {pipeline_count}\nSample: {', '.join(app_names) if app_names else 'none'}"
        elif response.status_code == 401 or response.status_code == 403:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Spinnaker error: {e}"

