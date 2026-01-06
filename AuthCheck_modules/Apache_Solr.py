# Apache Solr Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Solr (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8983",
     "port_toggle": "use_https", "tls_port": "8983", "non_tls_port": "8983"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Basic Auth", "Kerberos", "PKI"]},
    {"name": "username", "type": "text", "label": "Username", "default": "solr"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "ssl_cert", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 8983 (TLS/non-TLS same). solr / SolrRocks"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Solr using pysolr or REST API.
    """
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    scheme = "https" if use_https else "http"
    port_num = port if port else "8983"
    base_url = f"{scheme}://{host}:{port_num}/solr"
    
    # Try pysolr first
    try:
        import pysolr
        
        solr_kwargs = {
            'always_commit': False,
            'timeout': 10,
        }
        
        if auth_type == "Basic Auth" and username:
            solr_kwargs['auth'] = (username, password)
        
        if not verify_ssl:
            solr_kwargs['verify'] = False
        
        # Connect to admin endpoint
        solr = pysolr.Solr(f"{base_url}/admin/info", **solr_kwargs)
        
        # Ping to verify connection
        result = solr.ping()
        
        # Get system info via direct request
        import requests
        from requests.auth import HTTPBasicAuth
        
        auth = HTTPBasicAuth(username, password) if auth_type == "Basic Auth" and username else None
        
        info_url = f"{base_url}/admin/info/system"
        response = requests.get(info_url, auth=auth, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('lucene', {}).get('solr-spec-version', 'unknown')
            mode = data.get('mode', 'unknown')
            
            # Get cores
            cores_url = f"{base_url}/admin/cores"
            cores_response = requests.get(cores_url, auth=auth, verify=verify_ssl, timeout=10)
            cores = []
            if cores_response.status_code == 200:
                cores_data = cores_response.json()
                cores = list(cores_data.get('status', {}).keys())
            
            return True, f"Successfully connected to Apache Solr {version}\nMode: {mode}\nCores: {cores}"
        
    except ImportError:
        pass  # Fall through to requests-only approach
    except Exception as e:
        # If pysolr fails, try requests
        pass
    
    # Fallback to requests
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "pysolr or requests package not installed. Run: pip install pysolr"
    
    try:
        auth = None
        if auth_type == "Basic Auth" and username:
            auth = HTTPBasicAuth(username, password)
        
        # Get admin info
        url = f"{base_url}/admin/info/system"
        response = requests.get(url, auth=auth, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('lucene', {}).get('solr-spec-version', 'unknown')
            mode = data.get('mode', 'unknown')
            
            # Get cores/collections
            cores_url = f"{base_url}/admin/cores"
            cores_response = requests.get(cores_url, auth=auth, verify=verify_ssl, timeout=10)
            cores = []
            if cores_response.status_code == 200:
                cores_data = cores_response.json()
                cores = list(cores_data.get('status', {}).keys())
            
            return True, f"Successfully connected to Apache Solr {version}\nMode: {mode}\nCores: {cores}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Solr error: {e}"
