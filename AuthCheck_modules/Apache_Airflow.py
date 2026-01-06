# Apache Airflow Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Airflow (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Webserver Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "8080"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["Basic Auth", "Session/Cookie", "Kerberos", "OAuth"]},
    {"name": "username", "type": "text", "label": "Username", "default": "airflow"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 443, Non-TLS: 8080. airflow / airflow"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Airflow.
    """
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'Basic Auth')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Webserver Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "8080"
        base_url = f"{scheme}://{host}:{port_num}"
        
        session = requests.Session()
        
        if auth_type == "Basic Auth":
            session.auth = HTTPBasicAuth(username, password)
        elif auth_type == "Session/Cookie":
            # Login via web form
            login_url = f"{base_url}/login/"
            login_data = {
                'username': username,
                'password': password,
            }
            response = session.post(login_url, data=login_data, verify=verify_ssl, timeout=10)
            if response.status_code not in [200, 302]:
                return False, f"Login failed: HTTP {response.status_code}"
        
        # Try API endpoint
        api_url = f"{base_url}/api/v1/health"
        response = session.get(api_url, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            health = response.json()
            
            # Get version
            version_url = f"{base_url}/api/v1/version"
            ver_response = session.get(version_url, verify=verify_ssl, timeout=10)
            version = ver_response.json().get('version', 'unknown') if ver_response.status_code == 200 else 'unknown'
            
            metadb = health.get('metadatabase', {}).get('status', 'unknown')
            scheduler = health.get('scheduler', {}).get('status', 'unknown')
            
            return True, f"Successfully authenticated to Apache Airflow {version}\nMetadatabase: {metadb}, Scheduler: {scheduler}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Airflow error: {e}"

