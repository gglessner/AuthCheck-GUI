# Apache Druid Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Druid (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Router Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Router Port", "default": "8888",
     "port_toggle": "use_https", "tls_port": "8888", "non_tls_port": "8888"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Basic Auth", "Kerberos"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Router: 8888 (TLS/non-TLS same). druid_system / password"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Druid using pydruid or REST API.
    """
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Router Host is required"
    
    scheme = "https" if use_https else "http"
    port_num = port if port else "8888"
    base_url = f"{scheme}://{host}:{port_num}"
    
    # Try pydruid first
    try:
        from pydruid.db import connect
        from pydruid.client import PyDruid
        
        # Build connection parameters
        conn_kwargs = {
            'host': host,
            'port': int(port_num),
            'path': '/druid/v2/sql/',
            'scheme': scheme,
        }
        
        if auth_type == "Basic Auth" and username:
            # pydruid uses requests session for auth
            import requests
            from requests.auth import HTTPBasicAuth
            
            session = requests.Session()
            session.auth = HTTPBasicAuth(username, password)
            session.verify = verify_ssl
            
            # Create PyDruid client with session
            druid = PyDruid(base_url, 'druid/v2')
            
            # Test with a simple query to datasources
            datasources = druid.datasources()
            
            # Get status
            status_response = session.get(f"{base_url}/status", timeout=10)
            if status_response.status_code == 200:
                status_data = status_response.json()
                version = status_data.get('version', 'unknown')
                return True, f"Successfully connected to Apache Druid {version}\nDatasources: {datasources}"
        else:
            druid = PyDruid(base_url, 'druid/v2')
            datasources = druid.datasources()
            
            import requests
            status_response = requests.get(f"{base_url}/status", verify=verify_ssl, timeout=10)
            if status_response.status_code == 200:
                version = status_response.json().get('version', 'unknown')
                return True, f"Successfully connected to Apache Druid {version}\nDatasources: {datasources}"
            
    except ImportError:
        pass  # Fall through to requests
    except Exception as e:
        # Continue to requests fallback
        pass
    
    # Fallback to requests
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "pydruid or requests package not installed. Run: pip install pydruid"
    
    try:
        auth = None
        if auth_type == "Basic Auth" and username:
            auth = HTTPBasicAuth(username, password)
        
        # Get cluster status
        url = f"{base_url}/status"
        response = requests.get(url, auth=auth, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('version', 'unknown')
            
            # Get datasources
            ds_url = f"{base_url}/druid/v2/datasources"
            ds_response = requests.get(ds_url, auth=auth, verify=verify_ssl, timeout=10)
            datasources = ds_response.json() if ds_response.status_code == 200 else []
            
            return True, f"Successfully connected to Apache Druid {version}\nDatasources: {datasources}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Druid error: {e}"
