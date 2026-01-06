# RabbitMQ Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "RabbitMQ (MQ)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "AMQP Port", "default": "5672",
     "port_toggle": "use_ssl", "tls_port": "5671", "non_tls_port": "5672"},
    {"name": "vhost", "type": "text", "label": "Virtual Host", "default": "/"},
    {"name": "use_ssl", "type": "checkbox", "label": "Enable SSL/TLS"},
    {"name": "username", "type": "text", "label": "Username", "default": "guest"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "ssl_ca", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "ssl_cert", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "ssl_key", "type": "file", "label": "Client Key", "filter": "Key Files (*.pem *.key);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 5671, Non-TLS: 5672. guest / guest (localhost only), admin / admin"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to RabbitMQ.
    """
    try:
        import pika
    except ImportError:
        return False, "pika package not installed. Run: pip install pika"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    vhost = form_data.get('vhost', '/').strip()
    use_ssl = form_data.get('use_ssl', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    ssl_ca = form_data.get('ssl_ca', '').strip()
    ssl_cert = form_data.get('ssl_cert', '').strip()
    ssl_key = form_data.get('ssl_key', '').strip()
    
    if not host:
        return False, "Host is required"
    if not port:
        return False, "Port is required"
    
    try:
        credentials = pika.PlainCredentials(username, password)
        
        ssl_options = None
        if use_ssl:
            import ssl
            context = ssl.create_default_context()
            if ssl_ca:
                context.load_verify_locations(ssl_ca)
            if ssl_cert and ssl_key:
                context.load_cert_chain(ssl_cert, ssl_key)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            ssl_options = pika.SSLOptions(context, host)
        
        parameters = pika.ConnectionParameters(
            host=host,
            port=int(port),
            virtual_host=vhost,
            credentials=credentials,
            ssl_options=ssl_options,
            connection_attempts=1,
            socket_timeout=10
        )
        
        connection = pika.BlockingConnection(parameters)
        
        if connection.is_open:
            # Get server properties
            server_props = connection.server_properties
            product = server_props.get('product', b'RabbitMQ').decode() if isinstance(server_props.get('product'), bytes) else 'RabbitMQ'
            version = server_props.get('version', b'unknown').decode() if isinstance(server_props.get('version'), bytes) else 'unknown'
            
            connection.close()
            return True, f"Successfully authenticated to {product} {version} at {host}:{port} (vhost: {vhost})"
        else:
            return False, "Connection established but not open"
            
    except pika.exceptions.AMQPConnectionError as e:
        return False, f"AMQP connection error: {e}"
    except pika.exceptions.AuthenticationError:
        return False, "Authentication failed: Invalid credentials"
    except Exception as e:
        return False, f"Error: {e}"

