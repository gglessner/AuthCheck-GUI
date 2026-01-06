# Apache OpenMeetings Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache OpenMeetings (Collaboration)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "5443",
     "port_toggle": "use_https", "tls_port": "5443", "non_tls_port": "5080"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 5443, Non-TLS: 5080. admin / 1Q2w3e4r"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache OpenMeetings.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
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
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "5443"
        base_url = f"{scheme}://{host}:{port_num}/openmeetings/services"
        
        # Login via REST API
        login_url = f"{base_url}/user/login"
        params = {
            "user": username,
            "pass": password
        }
        
        response = requests.get(login_url, params=params, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('serviceResult', {}).get('type') == 'SUCCESS':
                result = data.get('serviceResult', {})
                message = result.get('message', '')
                
                # Parse session ID from message if available
                session_info = message if message else "Session established"
                
                return True, f"Successfully authenticated to Apache OpenMeetings at {host}:{port_num}\n{session_info}"
            else:
                error = data.get('serviceResult', {}).get('message', 'Authentication failed')
                return False, f"Authentication failed: {error}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"OpenMeetings error: {e}"

