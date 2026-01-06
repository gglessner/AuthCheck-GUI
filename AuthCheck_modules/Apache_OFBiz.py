# Apache OFBiz Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache OFBiz (ERP)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8443",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "webapp", "type": "text", "label": "WebApp", "default": "webtools"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8443, Non-TLS: 8080. admin / ofbiz"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache OFBiz.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', True)
    webapp = form_data.get('webapp', 'webtools').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "8443"
        base_url = f"{scheme}://{host}:{port_num}/{webapp}"
        
        session = requests.Session()
        
        # Get login page first
        login_page = session.get(f"{base_url}/control/main", verify=verify_ssl, timeout=10)
        
        # Login
        login_url = f"{base_url}/control/login"
        login_data = {
            "USERNAME": username,
            "PASSWORD": password
        }
        
        response = session.post(login_url, data=login_data, verify=verify_ssl, timeout=10, allow_redirects=True)
        
        if response.status_code == 200:
            # Check if we're logged in by looking for logout link or user info
            if 'logout' in response.text.lower() or 'Logged in as' in response.text:
                return True, f"Successfully authenticated to Apache OFBiz at {host}:{port_num}\nWebApp: {webapp}"
            elif 'error' in response.text.lower() or 'invalid' in response.text.lower():
                return False, "Authentication failed: Invalid credentials"
            else:
                # May still be successful
                cookies = session.cookies.get_dict()
                if any('JSESSIONID' in k for k in cookies.keys()):
                    return True, f"Successfully authenticated to Apache OFBiz at {host}:{port_num}"
                return False, "Authentication status unclear"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"OFBiz error: {e}"

