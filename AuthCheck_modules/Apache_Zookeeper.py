# Apache Zookeeper Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Zookeeper (Middleware)"

form_fields = [
    {"name": "hosts", "type": "text", "label": "Hosts (comma-sep)", "default": "localhost:2181"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Digest", "SASL"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "use_ssl", "type": "checkbox", "label": "Enable SSL/TLS"},
    {"name": "ssl_ca", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "ssl_cert", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "ssl_key", "type": "file", "label": "Client Key", "filter": "Key Files (*.pem *.key);;All Files (*)"},
    {"name": "timeout", "type": "text", "label": "Timeout (seconds)", "default": "10"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 2281, Non-TLS: 2181. Digest: admin / admin, zookeeper / zookeeper"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Zookeeper.
    """
    try:
        from kazoo.client import KazooClient
        from kazoo.security import make_digest_acl_credential
    except ImportError:
        return False, "kazoo package not installed. Run: pip install kazoo"
    
    hosts = form_data.get('hosts', '').strip()
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    use_ssl = form_data.get('use_ssl', False)
    ssl_ca = form_data.get('ssl_ca', '').strip()
    ssl_cert = form_data.get('ssl_cert', '').strip()
    ssl_key = form_data.get('ssl_key', '').strip()
    timeout = form_data.get('timeout', '10').strip()
    
    if not hosts:
        return False, "Hosts is required"
    
    try:
        timeout_sec = float(timeout) if timeout else 10.0
    except ValueError:
        return False, "Invalid timeout value"
    
    try:
        kwargs = {
            'hosts': hosts,
            'timeout': timeout_sec,
            'connection_retry': {'max_tries': 1},
        }
        
        if use_ssl:
            import ssl
            ssl_context = ssl.create_default_context()
            if ssl_ca:
                ssl_context.load_verify_locations(ssl_ca)
            if ssl_cert and ssl_key:
                ssl_context.load_cert_chain(ssl_cert, ssl_key)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            kwargs['use_ssl'] = True
            kwargs['ssl_context'] = ssl_context
        
        auth_data = None
        if auth_type == "Digest" and username and password:
            auth_data = [("digest", f"{username}:{password}")]
        elif auth_type == "SASL":
            kwargs['sasl_options'] = {
                'mechanism': 'DIGEST-MD5',
                'username': username,
                'password': password,
            }
        
        if auth_data:
            kwargs['auth_data'] = auth_data
        
        zk = KazooClient(**kwargs)
        zk.start(timeout=timeout_sec)
        
        # Check connection state
        if zk.connected:
            # Try to get root node to verify access
            stat = zk.exists('/')
            zk.stop()
            zk.close()
            return True, f"Successfully connected to Zookeeper at {hosts}"
        else:
            zk.stop()
            zk.close()
            return False, "Connection established but not in connected state"
            
    except Exception as e:
        error_msg = str(e)
        if "AuthFailedError" in error_msg or "authentication" in error_msg.lower():
            return False, "Authentication failed: Invalid credentials"
        return False, f"Zookeeper error: {e}"

