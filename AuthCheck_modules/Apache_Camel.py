# Apache Camel (JMX) Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Camel / Hawtio (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Hawtio Port", "default": "8181",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8181"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8443, Non-TLS: 8181. Camel framework - check component auth."},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Camel via Hawtio console.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "8181"
        base_url = f"{scheme}://{host}:{port_num}/hawtio"
        
        session = requests.Session()
        
        # Try Hawtio login
        login_url = f"{base_url}/auth/login"
        login_data = {
            "username": username,
            "password": password
        }
        
        response = session.post(login_url, json=login_data, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            # Try to get Jolokia info (JMX)
            jolokia_url = f"{base_url}/jolokia/version"
            jolokia_response = session.get(jolokia_url, verify=verify_ssl, timeout=10)
            
            agent_version = 'unknown'
            if jolokia_response.status_code == 200:
                jolokia_data = jolokia_response.json()
                agent_version = jolokia_data.get('value', {}).get('agent', 'unknown')
            
            return True, f"Successfully authenticated to Hawtio at {host}:{port_num}\nJolokia Agent: {agent_version}"
        elif response.status_code == 403:
            return False, "Authentication failed: Invalid credentials"
        else:
            # Try Jolokia direct access
            jolokia_url = f"{scheme}://{host}:{port_num}/jolokia/version"
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(username, password) if username else None
            jolokia_response = requests.get(jolokia_url, auth=auth, verify=verify_ssl, timeout=10)
            
            if jolokia_response.status_code == 200:
                data = jolokia_response.json()
                agent = data.get('value', {}).get('agent', 'unknown')
                return True, f"Successfully connected to Jolokia at {host}:{port_num}\nAgent: {agent}"
            
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Camel/Hawtio error: {e}"

