# NetApp ONTAP Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "NetApp ONTAP (Storage)"

form_fields = [
    {"name": "host", "type": "text", "label": "Cluster Management LIF"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "verify_ssl", "tls_port": "443", "non_tls_port": "80"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "HTTPS: 443, HTTP: 80. admin / (set during setup)."},
]


def authenticate(form_data):
    """Attempt to authenticate to NetApp ONTAP."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Cluster Management LIF is required"
    if not username:
        return False, "Username is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        session.auth = (username, password)
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Get cluster info
        response = session.get(f"{host}/api/cluster", headers=headers, timeout=10)
        
        if response.status_code == 200:
            cluster_data = response.json()
            cluster_name = cluster_data.get('name', 'unknown')
            version = cluster_data.get('version', {}).get('full', 'unknown')
            
            # Get node count
            nodes_resp = session.get(f"{host}/api/cluster/nodes", headers=headers, timeout=10)
            node_count = 0
            if nodes_resp.status_code == 200:
                node_count = nodes_resp.json().get('num_records', 0)
            
            # Get SVM count
            svm_resp = session.get(f"{host}/api/svm/svms", headers=headers, timeout=10)
            svm_count = 0
            if svm_resp.status_code == 200:
                svm_count = svm_resp.json().get('num_records', 0)
            
            # Get aggregate count
            aggr_resp = session.get(f"{host}/api/storage/aggregates", headers=headers, timeout=10)
            aggr_count = 0
            if aggr_resp.status_code == 200:
                aggr_count = aggr_resp.json().get('num_records', 0)
            
            return True, f"Successfully authenticated to NetApp ONTAP\nCluster: {cluster_name}\nVersion: {version}\nNodes: {node_count}\nSVMs: {svm_count}\nAggregates: {aggr_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"NetApp ONTAP error: {e}"

