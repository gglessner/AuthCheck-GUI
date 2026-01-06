# CUPS Print Server Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "CUPS Print Server (Printer)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "631"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "root or lpadmin group user. IPP: 631 (HTTP/HTTPS)"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to CUPS Print Server.
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
    
    scheme = "https" if use_https else "http"
    base_url = f"{scheme}://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # Get CUPS info (no auth needed)
        info_url = f"{base_url}/"
        info_resp = session.get(info_url, timeout=10)
        
        version = "unknown"
        if info_resp.status_code == 200:
            import re
            match = re.search(r'CUPS\s+([\d.]+)', info_resp.text)
            if match:
                version = match.group(1)
        
        # Try accessing admin page (requires auth)
        from requests.auth import HTTPBasicAuth
        
        admin_url = f"{base_url}/admin"
        response = session.get(admin_url, auth=HTTPBasicAuth(username, password), timeout=15)
        
        if response.status_code == 200:
            # Get printer count
            printers_url = f"{base_url}/printers"
            printers_resp = session.get(printers_url, auth=HTTPBasicAuth(username, password), timeout=10)
            
            printer_count = 0
            if printers_resp.status_code == 200:
                import re
                matches = re.findall(r'/printers/([^"\'>\s]+)', printers_resp.text)
                printer_count = len(set(matches))
            
            return True, f"Successfully authenticated to CUPS {version} at {host}\nPrinters: {printer_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Access forbidden: User not in lpadmin group"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"CUPS error: {e}"

