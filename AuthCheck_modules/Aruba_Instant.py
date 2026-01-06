# Aruba Instant AP Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Aruba Instant AP (Wireless)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "instant.arubanetworks.com"},
    {"name": "port", "type": "text", "label": "Port", "default": "4343",
     "port_toggle": "use_https", "tls_port": "4343", "non_tls_port": "80"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "HTTPS: 4343. admin / (set during setup). Virtual Controller IP."},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Aruba Instant AP.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', True)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    scheme = "https" if use_https else "http"
    base_url = f"{scheme}://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # Login to Aruba Instant
        login_url = f"{base_url}/rest/login"
        login_data = {
            "user": username,
            "passwd": password
        }
        
        response = session.post(login_url, json=login_data, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('Status') == 'Success' or 'sid' in response.cookies:
                # Get system info
                info_url = f"{base_url}/rest/show-cmd?iap_ip_addr=&cmd=show%20version"
                info_resp = session.get(info_url, timeout=10)
                
                version = "unknown"
                if info_resp.status_code == 200:
                    info_data = info_resp.json()
                    version = info_data.get('Version', 'unknown')
                
                # Logout
                session.post(f"{base_url}/rest/logout", timeout=5)
                
                return True, f"Successfully authenticated to Aruba Instant AP\nVersion: {version}"
            else:
                return False, f"Login failed: {data.get('message', 'Unknown error')}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Aruba Instant error: {e}"

