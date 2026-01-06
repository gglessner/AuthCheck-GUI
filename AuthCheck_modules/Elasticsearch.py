# Elasticsearch Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Elasticsearch (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "9200",
     "port_toggle": "use_https", "tls_port": "9200", "non_tls_port": "9200"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Basic Auth", "API Key", "Bearer Token"]},
    {"name": "username", "type": "text", "label": "Username", "default": "elastic"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "api_key", "type": "password", "label": "API Key (id:key)"},
    {"name": "bearer_token", "type": "password", "label": "Bearer Token"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "ssl_ca", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 9200 (TLS/non-TLS same). elastic / elastic, elastic / changeme"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Elasticsearch.
    """
    try:
        from elasticsearch import Elasticsearch
    except ImportError:
        return False, "elasticsearch package not installed. Run: pip install elasticsearch"
    
    hosts = form_data.get('hosts', '').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    api_key = form_data.get('api_key', '').strip()
    bearer_token = form_data.get('bearer_token', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    ssl_ca = form_data.get('ssl_ca', '').strip()
    
    if not hosts:
        return False, "Hosts is required"
    
    try:
        # Parse hosts
        host_list = []
        for h in hosts.split(','):
            h = h.strip()
            if not h.startswith('http'):
                scheme = 'https' if use_https else 'http'
                h = f"{scheme}://{h}"
            host_list.append(h)
        
        es_kwargs = {
            'hosts': host_list,
            'verify_certs': verify_ssl,
            'request_timeout': 10,
        }
        
        if ssl_ca:
            es_kwargs['ca_certs'] = ssl_ca
        
        if auth_type == "Basic Auth" and username:
            es_kwargs['basic_auth'] = (username, password)
        elif auth_type == "API Key" and api_key:
            if ':' in api_key:
                api_id, api_secret = api_key.split(':', 1)
                es_kwargs['api_key'] = (api_id, api_secret)
            else:
                es_kwargs['api_key'] = api_key
        elif auth_type == "Bearer Token" and bearer_token:
            es_kwargs['bearer_auth'] = bearer_token
        
        es = Elasticsearch(**es_kwargs)
        
        # Get cluster info
        info = es.info()
        cluster_name = info.get('cluster_name', 'unknown')
        version = info.get('version', {}).get('number', 'unknown')
        
        es.close()
        
        return True, f"Successfully authenticated to Elasticsearch {version}\nCluster: {cluster_name}"
        
    except Exception as e:
        error_msg = str(e)
        if "AuthenticationException" in error_msg or "401" in error_msg:
            return False, "Authentication failed: Invalid credentials"
        if "AuthorizationException" in error_msg or "403" in error_msg:
            return False, "Authorization failed: Insufficient permissions"
        return False, f"Elasticsearch error: {e}"

