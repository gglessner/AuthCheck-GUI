# Chef Infra / Automate Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Chef Infra / Automate (CI/CD)"

form_fields = [
    {"name": "server_url", "type": "text", "label": "Chef Server URL"},
    {"name": "node_name", "type": "text", "label": "Client/Node Name"},
    {"name": "client_key", "type": "file", "label": "Client Key (PEM)", "filter": "PEM Files (*.pem);;All Files (*)"},
    {"name": "organization", "type": "text", "label": "Organization"},
    {"name": "automate_url", "type": "text", "label": "Automate URL (Alternative)"},
    {"name": "automate_token", "type": "password", "label": "Automate Token"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Client key from chef-server-ctl. Automate token from Settings > API Tokens."},
]


def authenticate(form_data):
    """Attempt to authenticate to Chef Server or Automate."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    server_url = form_data.get('server_url', '').strip()
    node_name = form_data.get('node_name', '').strip()
    client_key = form_data.get('client_key', '').strip()
    organization = form_data.get('organization', '').strip()
    automate_url = form_data.get('automate_url', '').strip()
    automate_token = form_data.get('automate_token', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        if automate_url and automate_token:
            # Chef Automate API
            if not automate_url.startswith('http'):
                automate_url = f"https://{automate_url}"
            automate_url = automate_url.rstrip('/')
            
            headers = {
                'api-token': automate_token,
                'Content-Type': 'application/json'
            }
            
            response = session.get(f"{automate_url}/api/v0/compliance/reporting/stats/summary",
                                  headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Get node count
                nodes_resp = session.post(
                    f"{automate_url}/api/v0/cfgmgmt/nodes/search",
                    headers=headers, json={}, timeout=10)
                node_count = 0
                if nodes_resp.status_code == 200:
                    node_count = len(nodes_resp.json())
                
                return True, f"Successfully authenticated to Chef Automate\nNodes: {node_count}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid token"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:200]}"
        
        elif server_url and node_name and client_key and organization:
            # Chef Server API with signed requests (simplified check)
            # Full implementation would require chef library for request signing
            return False, "Chef Server authentication requires the 'chef' Python library. Use Automate API instead."
        
        else:
            return False, "Automate URL+Token or Server URL+Node+Key+Org required"
            
    except Exception as e:
        return False, f"Chef error: {e}"

