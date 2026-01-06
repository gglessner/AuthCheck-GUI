# OPNsense Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "OPNsense (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "OPNsense Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "api_key", "type": "text", "label": "API Key"},
    {"name": "api_secret", "type": "password", "label": "API Secret"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: root/opnsense. API keys from System > Access > Users."},
]


def authenticate(form_data):
    """Attempt to authenticate to OPNsense."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
    api_key = form_data.get('api_key', '').strip()
    api_secret = form_data.get('api_secret', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "OPNsense Host is required"
    if not api_key:
        return False, "API Key is required"
    if not api_secret:
        return False, "API Secret is required"
    
    try:
        base_url = f"https://{host}:{port}"
        
        # Get firmware status
        response = requests.get(
            f"{base_url}/api/core/firmware/status",
            auth=(api_key, api_secret),
            verify=verify_ssl,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('product_version', 'unknown')
            product = data.get('product_name', 'OPNsense')
            
            # Get interface info
            iface_resp = requests.get(
                f"{base_url}/api/interfaces/overview/export",
                auth=(api_key, api_secret),
                verify=verify_ssl,
                timeout=10
            )
            iface_count = 0
            if iface_resp.status_code == 200:
                iface_data = iface_resp.json()
                iface_count = len(iface_data.get('rows', []))
            
            return True, f"Successfully authenticated to OPNsense\nHost: {host}\nProduct: {product}\nVersion: {version}\nInterfaces: {iface_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"OPNsense error: {e}"

