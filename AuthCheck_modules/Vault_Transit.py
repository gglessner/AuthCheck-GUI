# HashiCorp Vault Transit Secrets Engine Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Vault Transit (Encryption)"

form_fields = [
    {"name": "url", "type": "text", "label": "Vault URL", "default": "http://localhost:8200"},
    {"name": "token", "type": "password", "label": "Token"},
    {"name": "transit_path", "type": "text", "label": "Transit Mount", "default": "transit"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Token auth (from Vault). Transit: encryption only"},
]


def authenticate(form_data):
    """Attempt to authenticate to Vault Transit engine."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', '').strip()
    token = form_data.get('token', '').strip()
    transit_path = form_data.get('transit_path', 'transit').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not url:
        return False, "Vault URL is required"
    if not token:
        return False, "Token is required"
    
    try:
        headers = {'X-Vault-Token': token}
        
        # List keys
        response = requests.request('LIST', f"{url}/v1/{transit_path}/keys",
                                   headers=headers, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            keys = data.get('data', {}).get('keys', [])
            
            return True, f"Successfully authenticated to Vault Transit\nMount: {transit_path}\nKeys: {keys}"
        elif response.status_code == 403:
            return False, "Authentication failed: Permission denied"
        elif response.status_code == 404:
            return False, f"Transit engine not found at '{transit_path}'"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, f"Vault error: {e}"

