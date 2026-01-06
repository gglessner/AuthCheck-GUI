# Nagios Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Nagios (Monitoring)"

form_fields = [
    {"name": "url", "type": "text", "label": "Nagios URL"},
    {"name": "username", "type": "text", "label": "Username", "default": "nagiosadmin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "api_key", "type": "password", "label": "API Key (XI)"},
    {"name": "version", "type": "combo", "label": "Version", "options": ["Nagios Core", "Nagios XI"], "default": "Nagios Core"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "nagiosadmin / (set during install). Nagios XI has REST API."},
]


def authenticate(form_data):
    """Attempt to authenticate to Nagios."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    api_key = form_data.get('api_key', '').strip()
    version = form_data.get('version', 'Nagios Core')
    
    if not url:
        return False, "Nagios URL is required"
    
    if not url.startswith('http'):
        url = f"http://{url}"
    url = url.rstrip('/')
    
    try:
        if version == "Nagios XI" and api_key:
            # Nagios XI API
            response = requests.get(f"{url}/nagiosxi/api/v1/system/status",
                                   params={'apikey': api_key}, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Get host count
                hosts_resp = requests.get(f"{url}/nagiosxi/api/v1/objects/host",
                                         params={'apikey': api_key}, timeout=10)
                host_count = 0
                if hosts_resp.status_code == 200:
                    host_count = hosts_resp.json().get('recordcount', 0)
                
                # Get service count
                services_resp = requests.get(f"{url}/nagiosxi/api/v1/objects/service",
                                            params={'apikey': api_key}, timeout=10)
                service_count = 0
                if services_resp.status_code == 200:
                    service_count = services_resp.json().get('recordcount', 0)
                
                return True, f"Successfully authenticated to Nagios XI\nHosts: {host_count}\nServices: {service_count}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid API key"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:200]}"
        else:
            # Nagios Core - Basic Auth
            if not username:
                return False, "Username is required"
            
            auth = HTTPBasicAuth(username, password)
            
            # Try to access CGI
            response = requests.get(f"{url}/nagios/cgi-bin/statusjson.cgi?query=programstatus",
                                   auth=auth, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    program_version = data.get('data', {}).get('programstatus', {}).get('nagios_version', 'unknown')
                except:
                    program_version = 'unknown'
                
                return True, f"Successfully authenticated to Nagios Core {program_version}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            else:
                # Try alternate URL
                alt_response = requests.get(f"{url}/nagios/", auth=auth, timeout=15)
                if alt_response.status_code == 200:
                    return True, f"Successfully authenticated to Nagios Core"
                return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Nagios error: {e}"

