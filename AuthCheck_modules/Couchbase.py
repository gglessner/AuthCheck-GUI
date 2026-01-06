# Couchbase Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Couchbase (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8091",
     "port_toggle": "use_ssl", "tls_port": "18091", "non_tls_port": "8091"},
    {"name": "bucket", "type": "text", "label": "Bucket"},
    {"name": "use_ssl", "type": "checkbox", "label": "Enable SSL"},
    {"name": "username", "type": "text", "label": "Username", "default": "Administrator"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 18091, Non-TLS: 8091. Administrator / (set during setup)"},
]


def authenticate(form_data):
    """Attempt to authenticate to Couchbase."""
    try:
        from couchbase.cluster import Cluster
        from couchbase.options import ClusterOptions
        from couchbase.auth import PasswordAuthenticator
    except ImportError:
        # Fallback to REST API
        pass
    else:
        host = form_data.get('host', '').strip()
        port = form_data.get('port', '8091').strip()
        bucket = form_data.get('bucket', '').strip()
        use_ssl = form_data.get('use_ssl', False)
        username = form_data.get('username', '').strip()
        password = form_data.get('password', '')
        
        if not host:
            return False, "Host is required"
        if not username:
            return False, "Username is required"
        
        try:
            scheme = "couchbases" if use_ssl else "couchbase"
            connection_string = f"{scheme}://{host}"
            
            auth = PasswordAuthenticator(username, password)
            cluster = Cluster(connection_string, ClusterOptions(auth))
            
            # Wait for cluster to be ready
            cluster.wait_until_ready(timeout=10)
            
            # Get cluster info
            ping_result = cluster.ping()
            
            if bucket:
                b = cluster.bucket(bucket)
                return True, f"Successfully authenticated to Couchbase at {host}\nBucket '{bucket}' accessible"
            
            return True, f"Successfully authenticated to Couchbase at {host}"
            
        except Exception as e:
            error_msg = str(e)
            if "authentication" in error_msg.lower():
                return False, f"Authentication failed: {e}"
            return False, f"Couchbase error: {e}"
    
    # REST API fallback
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "couchbase or requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8091').strip()
    use_ssl = form_data.get('use_ssl', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_ssl else "http"
        url = f"{scheme}://{host}:{port}/pools/default"
        
        auth = HTTPBasicAuth(username, password) if username else None
        response = requests.get(url, auth=auth, verify=False, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            cluster_name = data.get('clusterName', 'unknown')
            nodes = len(data.get('nodes', []))
            
            return True, f"Successfully authenticated to Couchbase\nCluster: {cluster_name}, Nodes: {nodes}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, f"Couchbase error: {e}"

