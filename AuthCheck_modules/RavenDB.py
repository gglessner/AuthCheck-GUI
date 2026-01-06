# RavenDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "RavenDB (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "RavenDB Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "8080",
     "port_toggle": "use_ssl", "tls_port": "443", "non_tls_port": "8080"},
    {"name": "certificate_file", "type": "file", "label": "Client Certificate (PFX)", "file_filter": "Certificate Files (*.pfx *.pem)"},
    {"name": "certificate_password", "type": "password", "label": "Certificate Password"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 443, Non-TLS: 8080. Secured requires client certificate."},
]


def authenticate(form_data):
    """Attempt to authenticate to RavenDB."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8080').strip()
    certificate_file = form_data.get('certificate_file', '').strip()
    certificate_password = form_data.get('certificate_password', '')
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "RavenDB Host is required"
    
    try:
        scheme = "https" if use_ssl else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        session = requests.Session()
        
        if certificate_file:
            if certificate_file.endswith('.pfx'):
                # Convert PFX to PEM for requests
                return False, "PFX certificates require conversion to PEM format"
            else:
                session.cert = certificate_file
        
        # Get build info
        response = session.get(
            f"{base_url}/build/version",
            timeout=15,
            verify=False
        )
        
        if response.status_code == 200:
            build_info = response.json()
            version = build_info.get('Version', 'unknown')
            build = build_info.get('BuildVersion', 'unknown')
            
            # Get databases
            dbs_resp = session.get(
                f"{base_url}/databases",
                timeout=10,
                verify=False
            )
            db_count = 0
            db_names = []
            if dbs_resp.status_code == 200:
                dbs = dbs_resp.json().get('Databases', [])
                db_count = len(dbs)
                db_names = [d.get('Name', 'unknown') for d in dbs[:5]]
            
            # Get cluster info
            cluster_resp = session.get(
                f"{base_url}/cluster/topology",
                timeout=10,
                verify=False
            )
            node_count = 0
            if cluster_resp.status_code == 200:
                cluster = cluster_resp.json().get('Topology', {})
                members = cluster.get('Members', {})
                node_count = len(members)
            
            return True, f"Successfully authenticated to RavenDB\nHost: {host}:{port}\nVersion: {version} (Build {build})\nNodes: {node_count}\nDatabases: {db_count}\nSample: {', '.join(db_names) if db_names else 'none'}"
        elif response.status_code == 401 or response.status_code == 403:
            return False, "Authentication failed: Certificate required"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"RavenDB error: {e}"

