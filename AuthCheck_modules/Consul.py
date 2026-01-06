# HashiCorp Consul Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "HashiCorp Consul (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8500",
     "port_toggle": "use_https", "tls_port": "8501", "non_tls_port": "8500"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "acl_token", "type": "password", "label": "ACL Token"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "ssl_ca", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "ssl_cert", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "ssl_key", "type": "file", "label": "Client Key", "filter": "Key Files (*.pem *.key);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8501, Non-TLS: 8500. Default: no ACL. Bootstrap token."},
]


def authenticate(form_data):
    """
    Attempt to authenticate to HashiCorp Consul.
    """
    try:
        import consul
    except ImportError:
        # Fall back to requests
        consul = None
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    acl_token = form_data.get('acl_token', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    ssl_ca = form_data.get('ssl_ca', '').strip()
    
    if not host:
        return False, "Host is required"
    
    port_num = int(port) if port else 8500
    scheme = "https" if use_https else "http"
    
    if consul:
        try:
            c = consul.Consul(
                host=host,
                port=port_num,
                scheme=scheme,
                token=acl_token if acl_token else None,
                verify=ssl_ca if ssl_ca else verify_ssl
            )
            
            # Get agent info
            agent_info = c.agent.self()
            version = agent_info.get('Config', {}).get('Version', 'unknown')
            datacenter = agent_info.get('Config', {}).get('Datacenter', 'unknown')
            node_name = agent_info.get('Config', {}).get('NodeName', 'unknown')
            
            return True, f"Successfully authenticated to Consul {version}\nDatacenter: {datacenter}, Node: {node_name}"
            
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg or "ACL" in error_msg:
                return False, f"Authentication failed: {e}"
            return False, f"Consul error: {e}"
    
    # Fallback to requests
    try:
        import requests
    except ImportError:
        return False, "python-consul or requests package not installed"
    
    try:
        url = f"{scheme}://{host}:{port_num}/v1/agent/self"
        headers = {}
        if acl_token:
            headers['X-Consul-Token'] = acl_token
        
        verify = ssl_ca if ssl_ca else verify_ssl
        response = requests.get(url, headers=headers, verify=verify, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('Config', {}).get('Version', 'unknown')
            datacenter = data.get('Config', {}).get('Datacenter', 'unknown')
            return True, f"Successfully authenticated to Consul {version}\nDatacenter: {datacenter}"
        elif response.status_code == 403:
            return False, "Authentication failed: ACL token required or invalid"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Consul error: {e}"

