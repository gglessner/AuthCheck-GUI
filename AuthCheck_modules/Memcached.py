# Memcached Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Memcached (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "11211",
     "port_toggle": "use_tls", "tls_port": "11212", "non_tls_port": "11211"},
    {"name": "use_tls", "type": "checkbox", "label": "Enable TLS"},
    {"name": "use_sasl", "type": "checkbox", "label": "Enable SASL Auth"},
    {"name": "username", "type": "text", "label": "SASL Username"},
    {"name": "password", "type": "password", "label": "SASL Password"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 11212, Non-TLS: 11211. SASL: memcached / memcached"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Memcached.
    """
    try:
        from pymemcache.client.base import Client
        from pymemcache.client.hash import HashClient
    except ImportError:
        return False, "pymemcache package not installed. Run: pip install pymemcache"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_tls = form_data.get('use_tls', False)
    use_sasl = form_data.get('use_sasl', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    if not host:
        return False, "Host is required"
    
    try:
        port_num = int(port) if port else 11211
        
        client_kwargs = {
            'connect_timeout': 10,
            'timeout': 10,
        }
        
        if use_tls:
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            client_kwargs['tls_context'] = ssl_context
        
        client = Client((host, port_num), **client_kwargs)
        
        # Get stats to verify connection
        stats = client.stats()
        
        if stats:
            version = stats.get(b'version', b'unknown').decode()
            uptime = stats.get(b'uptime', b'0').decode()
            curr_items = stats.get(b'curr_items', b'0').decode()
            
            client.close()
            
            return True, f"Successfully connected to Memcached {version}\nUptime: {uptime}s, Items: {curr_items}"
        else:
            client.close()
            return False, "Connected but could not get stats"
            
    except Exception as e:
        error_msg = str(e)
        if "AUTH" in error_msg.upper():
            return False, f"Authentication failed: {e}"
        return False, f"Memcached error: {e}"

