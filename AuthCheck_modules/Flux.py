# Flux CD Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Flux CD (CI/CD)"

form_fields = [
    {"name": "host", "type": "text", "label": "Weave GitOps Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "9001"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "token", "type": "password", "label": "Bearer Token (Alternative)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Weave GitOps UI port 9001. Default: admin/(configured). Or use kubectl."},
]


def authenticate(form_data):
    """Attempt to authenticate to Flux CD (via Weave GitOps)."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '9001').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    token = form_data.get('token', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Weave GitOps Host is required"
    
    try:
        base_url = f"https://{host}:{port}"
        session = requests.Session()
        session.verify = verify_ssl
        
        if token:
            headers = {'Authorization': f'Bearer {token}'}
        else:
            if not username:
                return False, "Username or Token required"
            
            # Login
            login_resp = session.post(
                f"{base_url}/oauth2/sign_in",
                data={'username': username, 'password': password},
                timeout=15
            )
            
            if login_resp.status_code not in [200, 302]:
                return False, "Authentication failed: Invalid credentials"
            
            headers = {}
        
        # Get Flux objects
        response = session.get(
            f"{base_url}/v1/namespaces",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            namespaces = data.get('namespaces', [])
            ns_count = len(namespaces)
            
            # Get kustomizations
            kust_resp = session.get(
                f"{base_url}/v1/kustomizations",
                headers=headers,
                timeout=10
            )
            kust_count = 0
            if kust_resp.status_code == 200:
                kust_count = len(kust_resp.json().get('kustomizations', []))
            
            # Get sources
            sources_resp = session.get(
                f"{base_url}/v1/sources",
                headers=headers,
                timeout=10
            )
            source_count = 0
            if sources_resp.status_code == 200:
                source_count = len(sources_resp.json().get('sources', []))
            
            return True, f"Successfully authenticated to Flux CD (Weave GitOps)\nHost: {host}:{port}\nNamespaces: {ns_count}\nKustomizations: {kust_count}\nSources: {source_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Flux CD error: {e}"

