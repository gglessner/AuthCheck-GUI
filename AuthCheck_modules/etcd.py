# etcd Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "etcd (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "2379",
     "port_toggle": "use_https", "tls_port": "2379", "non_tls_port": "2379"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "ssl_ca", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "ssl_cert", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "ssl_key", "type": "file", "label": "Client Key", "filter": "Key Files (*.pem *.key);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 2379 (TLS/non-TLS same). Default: no auth. root / root"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to etcd.
    """
    try:
        import etcd3
    except ImportError:
        etcd3 = None
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    ssl_ca = form_data.get('ssl_ca', '').strip()
    ssl_cert = form_data.get('ssl_cert', '').strip()
    ssl_key = form_data.get('ssl_key', '').strip()
    
    if not host:
        return False, "Host is required"
    
    port_num = int(port) if port else 2379
    
    if etcd3:
        try:
            client_kwargs = {
                'host': host,
                'port': port_num,
                'timeout': 10,
            }
            
            if username:
                client_kwargs['user'] = username
                client_kwargs['password'] = password
            
            if ssl_ca:
                client_kwargs['ca_cert'] = ssl_ca
            if ssl_cert:
                client_kwargs['cert_cert'] = ssl_cert
            if ssl_key:
                client_kwargs['cert_key'] = ssl_key
            
            client = etcd3.client(**client_kwargs)
            
            # Get cluster status
            status = client.status()
            version = status.version
            leader = status.leader
            
            client.close()
            
            return True, f"Successfully connected to etcd {version}\nLeader ID: {leader}"
            
        except Exception as e:
            error_msg = str(e)
            if "authentication" in error_msg.lower() or "permission" in error_msg.lower():
                return False, f"Authentication failed: {e}"
            return False, f"etcd error: {e}"
    
    # Fallback to REST API
    try:
        import requests
    except ImportError:
        return False, "etcd3 or requests package not installed"
    
    try:
        scheme = "https" if use_https else "http"
        url = f"{scheme}://{host}:{port_num}/version"
        
        auth = (username, password) if username else None
        verify = ssl_ca if ssl_ca else (not use_https)
        
        response = requests.get(url, auth=auth, verify=verify, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('etcdserver', 'unknown')
            cluster = data.get('etcdcluster', 'unknown')
            return True, f"Successfully connected to etcd {version}\nCluster version: {cluster}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"etcd error: {e}"

