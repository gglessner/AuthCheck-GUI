# Redis Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Redis (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "6379",
     "port_toggle": "use_tls", "tls_port": "6380", "non_tls_port": "6379"},
    {"name": "use_tls", "type": "checkbox", "label": "Enable TLS/SSL"},
    {"name": "use_acl", "type": "checkbox", "label": "Use ACL (Redis 6+)"},
    {"name": "username", "type": "text", "label": "Username (ACL)", "default": "default"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "database", "type": "text", "label": "Database Number", "default": "0"},
    {"name": "ssl_certfile", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "ssl_keyfile", "type": "file", "label": "Client Key", "filter": "Key Files (*.pem *.key);;All Files (*)"},
    {"name": "ssl_ca_certs", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 6380, Non-TLS: 6379. Default: no auth, ACL: default / (empty)"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Redis.
    
    Args:
        form_data (dict): Form field values
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        import redis
    except ImportError:
        return False, "redis package not installed. Run: pip install redis"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_tls = form_data.get('use_tls', False)
    use_acl = form_data.get('use_acl', False)
    username = form_data.get('username', '').strip() if use_acl else None
    password = form_data.get('password', '') or None
    database = form_data.get('database', '0').strip()
    ssl_certfile = form_data.get('ssl_certfile', '').strip() or None
    ssl_keyfile = form_data.get('ssl_keyfile', '').strip() or None
    ssl_ca_certs = form_data.get('ssl_ca_certs', '').strip() or None
    
    if not host:
        return False, "Host is required"
    if not port:
        return False, "Port is required"
    
    try:
        db_num = int(database) if database else 0
    except ValueError:
        return False, "Database number must be an integer"
    
    try:
        connection_kwargs = {
            'host': host,
            'port': int(port),
            'db': db_num,
            'socket_timeout': 10,
            'socket_connect_timeout': 10,
        }
        
        if password:
            connection_kwargs['password'] = password
        
        if use_acl and username:
            connection_kwargs['username'] = username
        
        if use_tls:
            connection_kwargs['ssl'] = True
            if ssl_certfile:
                connection_kwargs['ssl_certfile'] = ssl_certfile
            if ssl_keyfile:
                connection_kwargs['ssl_keyfile'] = ssl_keyfile
            if ssl_ca_certs:
                connection_kwargs['ssl_ca_certs'] = ssl_ca_certs
        
        r = redis.Redis(**connection_kwargs)
        
        # Test the connection with a PING
        response = r.ping()
        
        if response:
            # Get some server info
            info = r.info('server')
            redis_version = info.get('redis_version', 'unknown')
            r.close()
            return True, f"Successfully authenticated to Redis {redis_version} at {host}:{port} (db: {db_num})"
        else:
            r.close()
            return False, "Connected but PING failed"
            
    except redis.AuthenticationError as e:
        return False, f"Authentication failed: {e}"
    except redis.ConnectionError as e:
        return False, f"Connection error: {e}"
    except Exception as e:
        return False, f"Error: {e}"
