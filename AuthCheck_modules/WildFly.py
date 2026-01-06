# WildFly/JBoss Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "WildFly / JBoss EAP (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "mgmt_port", "type": "text", "label": "Management Port", "default": "9990",
     "port_toggle": "use_https", "tls_port": "9993", "non_tls_port": "9990"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 9993, Non-TLS: 9990. admin / (set via add-user.sh)"},
]


def authenticate(form_data):
    """Attempt to authenticate to WildFly/JBoss management interface."""
    try:
        import requests
        from requests.auth import HTTPDigestAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    mgmt_port = form_data.get('mgmt_port', '9990').strip()
    use_https = form_data.get('use_https', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{host}:{mgmt_port}/management"
        
        # WildFly uses Digest auth
        auth = HTTPDigestAuth(username, password)
        
        # Read server state
        payload = {
            "operation": "read-attribute",
            "name": "product-version",
            "json.pretty": 1
        }
        
        response = requests.post(base_url, json=payload, auth=auth, 
                                verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('outcome') == 'success':
                version = data.get('result', 'unknown')
                
                # Get server state
                state_payload = {
                    "operation": "read-attribute",
                    "name": "server-state"
                }
                state_resp = requests.post(base_url, json=state_payload, auth=auth,
                                          verify=verify_ssl, timeout=10)
                state = 'unknown'
                if state_resp.status_code == 200:
                    state = state_resp.json().get('result', 'unknown')
                
                # Get deployments
                deploy_payload = {
                    "operation": "read-children-names",
                    "child-type": "deployment"
                }
                deploy_resp = requests.post(base_url, json=deploy_payload, auth=auth,
                                           verify=verify_ssl, timeout=10)
                deployments = []
                if deploy_resp.status_code == 200:
                    deployments = deploy_resp.json().get('result', [])
                
                return True, f"Successfully authenticated to WildFly {version}\nState: {state}\nDeployments: {len(deployments)}"
            else:
                return False, f"Management error: {data.get('failure-description', 'Unknown')}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, f"WildFly error: {e}"

