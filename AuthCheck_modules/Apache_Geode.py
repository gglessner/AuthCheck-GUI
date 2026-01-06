# Apache Geode Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Geode (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Locator Host", "default": "localhost"},
    {"name": "http_port", "type": "text", "label": "HTTP Port", "default": "7070",
     "port_toggle": "use_https", "tls_port": "7443", "non_tls_port": "7070"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 7443, Non-TLS: 7070. admin / admin"},
]


def authenticate(form_data):
    """
    Attempt to connect to Apache Geode via Pulse/REST API.
    """
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    http_port = form_data.get('http_port', '').strip()
    use_https = form_data.get('use_https', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Locator Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = http_port if http_port else "7070"
        base_url = f"{scheme}://{host}:{port_num}"
        
        auth = HTTPBasicAuth(username, password) if username else None
        
        # Try management REST API
        url = f"{base_url}/management/v1/ping"
        response = requests.get(url, auth=auth, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            # Get members
            members_url = f"{base_url}/management/v1/members"
            members_response = requests.get(members_url, auth=auth, verify=verify_ssl, timeout=10)
            members = []
            if members_response.status_code == 200:
                members = [m.get('id') for m in members_response.json().get('result', [])]
            
            # Get regions
            regions_url = f"{base_url}/management/v1/regions"
            regions_response = requests.get(regions_url, auth=auth, verify=verify_ssl, timeout=10)
            regions = []
            if regions_response.status_code == 200:
                regions = [r.get('name') for r in regions_response.json().get('result', [])]
            
            return True, f"Successfully connected to Apache Geode at {host}:{port_num}\nMembers: {members}\nRegions: {regions}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        elif response.status_code == 404:
            # Try Pulse
            pulse_url = f"{base_url}/pulse/login.html"
            pulse_response = requests.get(pulse_url, verify=verify_ssl, timeout=10)
            if pulse_response.status_code == 200:
                return True, f"Apache Geode Pulse accessible at {host}:{port_num}/pulse"
            return False, "Management API not found"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Geode error: {e}"

