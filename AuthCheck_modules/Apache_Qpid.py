# Apache Qpid Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Qpid (MQ)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "AMQP Port", "default": "5672",
     "port_toggle": "use_ssl", "tls_port": "5671", "non_tls_port": "5672"},
    {"name": "http_port", "type": "text", "label": "HTTP Port", "default": "8080",
     "port_toggle": "use_ssl", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "use_ssl", "type": "checkbox", "label": "Enable SSL"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS AMQP: 5671, HTTP: 8443. Non-TLS: 5672/8080. guest / guest"},
]


def authenticate(form_data):
    """Attempt to authenticate to Apache Qpid."""
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '5672').strip()
    http_port = form_data.get('http_port', '8080').strip()
    use_ssl = form_data.get('use_ssl', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    if not host:
        return False, "Host is required"
    
    # Try HTTP management API first
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        scheme = "https" if use_ssl else "http"
        base_url = f"{scheme}://{host}:{http_port}/api/latest"
        
        auth = HTTPBasicAuth(username, password) if username else None
        
        response = requests.get(f"{base_url}/broker", auth=auth, verify=False, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            model_version = data.get('modelVersion', 'unknown')
            broker_type = data.get('type', 'unknown')
            
            return True, f"Successfully authenticated to Apache Qpid\nType: {broker_type}\nModel Version: {model_version}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
    except:
        pass
    
    # Try AMQP
    try:
        import pika
        
        port_num = int(port) if port else 5672
        credentials = pika.PlainCredentials(username, password)
        
        ssl_options = None
        if use_ssl:
            import ssl
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            ssl_options = pika.SSLOptions(context, host)
        
        parameters = pika.ConnectionParameters(
            host=host,
            port=port_num,
            credentials=credentials,
            ssl_options=ssl_options,
            connection_attempts=1,
            socket_timeout=10
        )
        
        connection = pika.BlockingConnection(parameters)
        
        if connection.is_open:
            connection.close()
            return True, f"Successfully authenticated to Apache Qpid at {host}:{port_num} via AMQP"
        
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower():
            return False, f"Authentication failed: {e}"
        return False, f"Qpid error: {e}"
    
    return False, "Connection failed"

