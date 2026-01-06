# HashiCorp Nomad Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "HashiCorp Nomad (Container)"

form_fields = [
    {"name": "address", "type": "text", "label": "Nomad Address", "default": "http://localhost:4646"},
    {"name": "token", "type": "password", "label": "ACL Token"},
    {"name": "namespace", "type": "text", "label": "Namespace", "default": "default"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default port 4646. ACL token from 'nomad acl bootstrap' or Nomad UI."},
]


def authenticate(form_data):
    """Attempt to authenticate to HashiCorp Nomad."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    address = form_data.get('address', 'http://localhost:4646').strip()
    token = form_data.get('token', '').strip()
    namespace = form_data.get('namespace', 'default').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not address:
        return False, "Nomad Address is required"
    
    address = address.rstrip('/')
    
    try:
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['X-Nomad-Token'] = token
        
        # Get agent self info
        response = requests.get(f"{address}/v1/agent/self",
                               headers=headers, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            config = data.get('config', {})
            member = data.get('member', {})
            stats = data.get('stats', {})
            
            version = config.get('Version', 'unknown')
            datacenter = config.get('Datacenter', 'unknown')
            region = config.get('Region', 'unknown')
            node_name = member.get('Name', 'unknown')
            
            # Get job count
            jobs_resp = requests.get(f"{address}/v1/jobs",
                                    headers=headers, verify=verify_ssl, timeout=10)
            job_count = 0
            if jobs_resp.status_code == 200:
                job_count = len(jobs_resp.json())
            
            # Get node count
            nodes_resp = requests.get(f"{address}/v1/nodes",
                                     headers=headers, verify=verify_ssl, timeout=10)
            node_count = 0
            if nodes_resp.status_code == 200:
                node_count = len(nodes_resp.json())
            
            return True, f"Successfully authenticated to Nomad {version}\nDatacenter: {datacenter}\nRegion: {region}\nJobs: {job_count}\nNodes: {node_count}"
        elif response.status_code == 403:
            return False, "Authentication failed: Invalid or missing ACL token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Nomad error: {e}"

