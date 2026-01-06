# Apache NiFi Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache NiFi (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "NiFi Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8443",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["Username/Password", "Client Certificate", "OIDC Token"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "ssl_cert", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.crt *.p12);;All Files (*)"},
    {"name": "ssl_key", "type": "file", "label": "Client Key", "filter": "Key Files (*.pem *.key);;All Files (*)"},
    {"name": "ssl_ca", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL Certificate"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8443, Non-TLS: 8080. admin / (generated), nifi / nifi"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache NiFi.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', True)
    auth_type = form_data.get('auth_type', 'Username/Password')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    ssl_cert = form_data.get('ssl_cert', '').strip()
    ssl_key = form_data.get('ssl_key', '').strip()
    ssl_ca = form_data.get('ssl_ca', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "NiFi Host is required"
    if not port:
        return False, "Port is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{port}/nifi-api"
        
        session = requests.Session()
        
        verify = ssl_ca if ssl_ca else verify_ssl
        
        if auth_type == "Client Certificate" and ssl_cert:
            cert = (ssl_cert, ssl_key) if ssl_key else ssl_cert
            session.cert = cert
        
        # Try to get access token for username/password auth
        if auth_type == "Username/Password" and username:
            token_url = f"{base_url}/access/token"
            response = session.post(
                token_url,
                data={'username': username, 'password': password},
                verify=verify,
                timeout=10
            )
            
            if response.status_code == 201:
                token = response.text
                session.headers['Authorization'] = f'Bearer {token}'
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            else:
                # NiFi might not require authentication
                pass
        
        # Get system diagnostics
        diag_url = f"{base_url}/system-diagnostics"
        response = session.get(diag_url, verify=verify, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('systemDiagnostics', {}).get('aggregateSnapshot', {}).get('versionInfo', {}).get('niFiVersion', 'unknown')
            return True, f"Successfully authenticated to Apache NiFi {version} at {host}:{port}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            # Try a simpler endpoint
            flow_url = f"{base_url}/flow/about"
            response = session.get(flow_url, verify=verify, timeout=10)
            if response.status_code == 200:
                data = response.json()
                version = data.get('about', {}).get('version', 'unknown')
                return True, f"Successfully connected to Apache NiFi {version} at {host}:{port}"
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except requests.exceptions.SSLError as e:
        return False, f"SSL error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

