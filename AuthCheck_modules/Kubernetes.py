# Kubernetes API Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Kubernetes API (Container)"

form_fields = [
    {"name": "host", "type": "text", "label": "API Server Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "6443",
     "port_toggle": "verify_ssl", "tls_port": "6443", "non_tls_port": "8080"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["Bearer Token", "Client Certificate", "Kubeconfig"]},
    {"name": "token", "type": "password", "label": "Bearer Token"},
    {"name": "client_cert", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "client_key", "type": "file", "label": "Client Key", "filter": "Key Files (*.pem *.key);;All Files (*)"},
    {"name": "ca_cert", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "kubeconfig", "type": "file", "label": "Kubeconfig File", "filter": "Config Files (*.yaml *.yml config);;All Files (*)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "HTTPS: 6443, HTTP: 8080. Kubeconfig: ~/.kube/config"},
]


def authenticate(form_data):
    """Attempt to authenticate to Kubernetes API."""
    api_server = form_data.get('api_server', '').strip()
    auth_type = form_data.get('auth_type', 'Bearer Token')
    token = form_data.get('token', '').strip()
    client_cert = form_data.get('client_cert', '').strip()
    client_key = form_data.get('client_key', '').strip()
    ca_cert = form_data.get('ca_cert', '').strip()
    kubeconfig = form_data.get('kubeconfig', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if auth_type == "Kubeconfig":
        try:
            from kubernetes import client, config
        except ImportError:
            return False, "kubernetes package not installed. Run: pip install kubernetes"
        
        try:
            if kubeconfig:
                config.load_kube_config(config_file=kubeconfig)
            else:
                config.load_kube_config()
            
            v1 = client.CoreV1Api()
            version_api = client.VersionApi()
            
            version = version_api.get_code()
            namespaces = v1.list_namespace()
            ns_names = [ns.metadata.name for ns in namespaces.items]
            
            return True, f"Successfully authenticated to Kubernetes {version.git_version}\nNamespaces: {ns_names}"
        except Exception as e:
            return False, f"Kubernetes error: {e}"
    
    # Use requests for token/cert auth
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    if not api_server:
        return False, "API Server is required"
    
    try:
        headers = {}
        cert = None
        verify = ca_cert if ca_cert else verify_ssl
        
        if auth_type == "Bearer Token":
            if not token:
                return False, "Bearer Token is required"
            headers['Authorization'] = f"Bearer {token}"
        elif auth_type == "Client Certificate":
            if not client_cert or not client_key:
                return False, "Client Certificate and Key are required"
            cert = (client_cert, client_key)
        
        # Get version
        response = requests.get(f"{api_server}/version", headers=headers,
                               cert=cert, verify=verify, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('gitVersion', 'unknown')
            
            # Get namespaces
            ns_resp = requests.get(f"{api_server}/api/v1/namespaces", headers=headers,
                                  cert=cert, verify=verify, timeout=10)
            namespaces = []
            if ns_resp.status_code == 200:
                ns_data = ns_resp.json()
                namespaces = [ns.get('metadata', {}).get('name') 
                             for ns in ns_data.get('items', [])]
            
            return True, f"Successfully authenticated to Kubernetes {version}\nNamespaces: {namespaces}"
        elif response.status_code in [401, 403]:
            return False, "Authentication failed: Unauthorized"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, f"Kubernetes error: {e}"

