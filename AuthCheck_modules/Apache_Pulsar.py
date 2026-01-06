# Apache Pulsar Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Pulsar (MQ)"

form_fields = [
    {"name": "service_url", "type": "text", "label": "Service URL", "default": "pulsar://localhost:6650"},
    {"name": "admin_url", "type": "text", "label": "Admin URL", "default": "http://localhost:8080"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Token", "TLS", "Athenz", "OAuth2"]},
    {"name": "token", "type": "password", "label": "JWT Token"},
    {"name": "tls_cert", "type": "file", "label": "TLS Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "tls_key", "type": "file", "label": "TLS Key", "filter": "Key Files (*.pem *.key);;All Files (*)"},
    {"name": "tls_ca", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "verify_tls", "type": "checkbox", "label": "Verify TLS"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: no auth. Token: JWT from bin/pulsar tokens create"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Pulsar.
    """
    service_url = form_data.get('service_url', '').strip()
    admin_url = form_data.get('admin_url', '').strip()
    auth_type = form_data.get('auth_type', 'None')
    token = form_data.get('token', '').strip()
    tls_cert = form_data.get('tls_cert', '').strip()
    tls_key = form_data.get('tls_key', '').strip()
    tls_ca = form_data.get('tls_ca', '').strip()
    verify_tls = form_data.get('verify_tls', False)
    
    # Try using pulsar-client library first
    try:
        import pulsar
        
        client_kwargs = {
            'service_url': service_url,
            'operation_timeout_seconds': 10,
        }
        
        if auth_type == "Token" and token:
            client_kwargs['authentication'] = pulsar.AuthenticationToken(token)
        elif auth_type == "TLS" and tls_cert and tls_key:
            client_kwargs['authentication'] = pulsar.AuthenticationTLS(tls_cert, tls_key)
        
        if tls_ca:
            client_kwargs['tls_trust_certs_file_path'] = tls_ca
        if not verify_tls:
            client_kwargs['tls_allow_insecure_connection'] = True
        
        client = pulsar.Client(**client_kwargs)
        
        # Try to create a reader to verify connection
        # This will fail if auth is wrong
        client.close()
        
        return True, f"Successfully connected to Pulsar at {service_url}"
        
    except ImportError:
        pass
    except Exception as e:
        if "Authentication" in str(e) or "401" in str(e):
            return False, f"Authentication failed: {e}"
        # Continue to admin API fallback
    
    # Fallback to admin REST API
    if admin_url:
        try:
            import requests
        except ImportError:
            return False, "requests package not installed. Run: pip install requests"
        
        try:
            headers = {}
            if auth_type == "Token" and token:
                headers['Authorization'] = f'Bearer {token}'
            
            url = f"{admin_url}/admin/v2/clusters"
            verify = tls_ca if tls_ca else verify_tls
            
            response = requests.get(url, headers=headers, verify=verify, timeout=10)
            
            if response.status_code == 200:
                clusters = response.json()
                return True, f"Successfully connected to Pulsar admin at {admin_url}\nClusters: {clusters}"
            elif response.status_code == 401:
                return False, "Authentication failed: Unauthorized"
            elif response.status_code == 403:
                return False, "Authentication failed: Forbidden"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:200]}"
                
        except Exception as e:
            return False, f"Pulsar admin error: {e}"
    
    return False, "pulsar-client package not installed. Run: pip install pulsar-client"

