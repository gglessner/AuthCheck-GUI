# HashiCorp Vault Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "HashiCorp Vault (IAM)"

form_fields = [
    {"name": "host", "type": "text", "label": "Vault Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8200",
     "port_toggle": "verify_ssl", "tls_port": "8200", "non_tls_port": "8200"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_method", "type": "combo", "label": "Auth Method",
     "options": ["Token", "UserPass", "LDAP", "AppRole", "Kubernetes"]},
    {"name": "token", "type": "password", "label": "Token"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "role_id", "type": "text", "label": "AppRole Role ID"},
    {"name": "secret_id", "type": "password", "label": "AppRole Secret ID"},
    {"name": "namespace", "type": "text", "label": "Namespace"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "ssl_ca", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 8200 (TLS/non-TLS same). Token: root from init."},
]


def authenticate(form_data):
    """
    Attempt to authenticate to HashiCorp Vault.
    """
    try:
        import hvac
    except ImportError:
        return False, "hvac package not installed. Run: pip install hvac"
    
    url = form_data.get('url', '').strip()
    auth_method = form_data.get('auth_method', 'Token')
    token = form_data.get('token', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    role_id = form_data.get('role_id', '').strip()
    secret_id = form_data.get('secret_id', '').strip()
    namespace = form_data.get('namespace', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    ssl_ca = form_data.get('ssl_ca', '').strip()
    
    if not url:
        return False, "Vault URL is required"
    
    try:
        verify = ssl_ca if ssl_ca else verify_ssl
        
        client = hvac.Client(
            url=url,
            verify=verify,
            namespace=namespace if namespace else None
        )
        
        if auth_method == "Token":
            if not token:
                return False, "Token is required"
            client.token = token
            
        elif auth_method == "UserPass":
            if not username:
                return False, "Username is required"
            client.auth.userpass.login(username=username, password=password)
            
        elif auth_method == "LDAP":
            if not username:
                return False, "Username is required"
            client.auth.ldap.login(username=username, password=password)
            
        elif auth_method == "AppRole":
            if not role_id:
                return False, "Role ID is required"
            client.auth.approle.login(role_id=role_id, secret_id=secret_id)
            
        elif auth_method == "Kubernetes":
            return False, "Kubernetes auth requires service account token - not supported in this context"
        
        # Verify authentication
        if client.is_authenticated():
            # Get token info
            token_info = client.auth.token.lookup_self()
            policies = token_info.get('data', {}).get('policies', [])
            
            # Get Vault status
            status = client.sys.read_health_status(method='GET')
            version = status.get('version', 'unknown')
            cluster_name = status.get('cluster_name', 'unknown')
            
            return True, f"Successfully authenticated to Vault {version}\nCluster: {cluster_name}\nPolicies: {policies}"
        else:
            return False, "Authentication failed: Token not valid"
            
    except hvac.exceptions.InvalidRequest as e:
        return False, f"Invalid request: {e}"
    except hvac.exceptions.Unauthorized as e:
        return False, f"Authentication failed: {e}"
    except hvac.exceptions.Forbidden as e:
        return False, f"Authorization failed: {e}"
    except Exception as e:
        return False, f"Vault error: {e}"

