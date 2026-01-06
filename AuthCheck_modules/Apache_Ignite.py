# Apache Ignite Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Ignite (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "thin_client_port", "type": "text", "label": "Thin Client Port", "default": "10800",
     "port_toggle": "use_ssl", "tls_port": "10801", "non_tls_port": "10800"},
    {"name": "rest_port", "type": "text", "label": "REST Port", "default": "8080",
     "port_toggle": "use_ssl", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "protocol", "type": "combo", "label": "Protocol",
     "options": ["Thin Client (pyignite)", "REST API"]},
    {"name": "use_ssl", "type": "checkbox", "label": "Enable SSL/TLS"},
    {"name": "auth_enabled", "type": "checkbox", "label": "Authentication Enabled"},
    {"name": "username", "type": "text", "label": "Username", "default": "ignite"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 10801/8443, Non-TLS: 10800/8080. ignite / ignite"},
]


def authenticate(form_data):
    """
    Attempt to connect to Apache Ignite using pyignite thin client or REST API.
    """
    host = form_data.get('host', '').strip()
    thin_client_port = form_data.get('thin_client_port', '10800').strip()
    rest_port = form_data.get('rest_port', '8080').strip()
    protocol = form_data.get('protocol', 'Thin Client (pyignite)')
    use_ssl = form_data.get('use_ssl', False)
    auth_enabled = form_data.get('auth_enabled', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    if protocol == "Thin Client (pyignite)":
        try:
            from pyignite import Client
        except ImportError:
            return False, "pyignite package not installed. Run: pip install pyignite"
        
        try:
            port = int(thin_client_port) if thin_client_port else 10800
            
            client = Client()
            
            # Configure SSL if enabled
            if use_ssl:
                client = Client(
                    use_ssl=True,
                    ssl_certfile=None,
                    ssl_keyfile=None,
                    ssl_ca_certfile=None,
                    ssl_cert_reqs='CERT_NONE' if not verify_ssl else 'CERT_REQUIRED'
                )
            
            # Configure authentication if enabled
            if auth_enabled and username:
                client = Client(
                    username=username,
                    password=password,
                    use_ssl=use_ssl
                )
            
            client.connect(host, port)
            
            # Get cluster state
            from pyignite.datatypes.cluster_state import ClusterState
            cluster_state = client.cluster.get_state()
            
            # Get nodes
            nodes = list(client.get_node_info())
            node_count = len(nodes)
            
            # Get caches
            caches = client.get_cache_names()
            
            client.close()
            
            state_name = {0: 'INACTIVE', 1: 'ACTIVE', 2: 'ACTIVE_READ_ONLY'}.get(cluster_state, 'UNKNOWN')
            
            return True, f"Successfully connected to Apache Ignite via Thin Client\nCluster State: {state_name}\nNodes: {node_count}, Caches: {len(caches)}"
            
        except Exception as e:
            error_msg = str(e)
            if "authentication" in error_msg.lower() or "AuthorizationError" in error_msg:
                return False, f"Authentication failed: {e}"
            return False, f"Ignite Thin Client error: {e}"
    
    else:  # REST API
        try:
            import requests
        except ImportError:
            return False, "requests package not installed. Run: pip install requests"
        
        try:
            scheme = "https" if use_ssl else "http"
            port_num = rest_port if rest_port else "8080"
            base_url = f"{scheme}://{host}:{port_num}/ignite"
            
            params = {}
            if auth_enabled and username:
                params['user'] = username
                params['password'] = password
            
            # Get cluster state
            url = f"{base_url}?cmd=state"
            response = requests.get(url, params=params, verify=verify_ssl, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('successStatus') == 0:
                    state = data.get('response', 'unknown')
                    
                    # Get version
                    ver_url = f"{base_url}?cmd=version"
                    ver_response = requests.get(ver_url, params=params, verify=verify_ssl, timeout=10)
                    version = 'unknown'
                    if ver_response.status_code == 200:
                        ver_data = ver_response.json()
                        if ver_data.get('successStatus') == 0:
                            version = ver_data.get('response', 'unknown')
                    
                    # Get topology
                    top_url = f"{base_url}?cmd=top&attr=true"
                    top_response = requests.get(top_url, params=params, verify=verify_ssl, timeout=10)
                    nodes = 0
                    if top_response.status_code == 200:
                        top_data = top_response.json()
                        if top_data.get('successStatus') == 0:
                            nodes = len(top_data.get('response', []))
                    
                    return True, f"Successfully connected to Apache Ignite {version} via REST\nCluster State: {state}\nNodes: {nodes}"
                else:
                    return False, f"Ignite error: {data.get('error', 'Unknown error')}"
            elif response.status_code == 401:
                return False, "Authentication failed: Unauthorized"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:200]}"
                
        except Exception as e:
            return False, f"Ignite REST error: {e}"
