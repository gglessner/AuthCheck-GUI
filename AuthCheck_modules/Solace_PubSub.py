# Solace PubSub+ Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Solace PubSub+ (MQ)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "SMF Port", "default": "55443",
     "port_toggle": "use_tls", "tls_port": "55443", "non_tls_port": "55555"},
    {"name": "vpn", "type": "text", "label": "Message VPN", "default": "default"},
    {"name": "use_tls", "type": "checkbox", "label": "Enable TLS", "default": True},
    {"name": "auth_type", "type": "combo", "label": "Authentication Type",
     "options": ["Basic", "Client Certificate", "Kerberos", "OAuth"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "trust_store", "type": "file", "label": "Trust Store", "filter": "Certificate Files (*.pem *.crt *.jks);;All Files (*)"},
    {"name": "client_cert", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "client_key", "type": "file", "label": "Client Key", "filter": "Key Files (*.pem *.key);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 55443, Non-TLS: 55555. admin / admin, default / default, solace / solace"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Solace PubSub+.
    
    Args:
        form_data (dict): Form field values
        
    Returns:
        tuple: (success: bool, message: str)
    """
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    vpn = form_data.get('vpn', '').strip()
    use_tls = form_data.get('use_tls', False)
    auth_type = form_data.get('auth_type', 'Basic')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    if not host:
        return False, "Host is required"
    if not port:
        return False, "Port is required"
    if not vpn:
        return False, "Message VPN is required"
    
    # Try using solace-pubsubplus if available
    try:
        from solace.messaging.messaging_service import MessagingService
        from solace.messaging.config.retry_strategy import RetryStrategy
        
        protocol = "tcps" if use_tls else "tcp"
        broker_props = {
            "solace.messaging.transport.host": f"{protocol}://{host}:{port}",
            "solace.messaging.service.vpn-name": vpn,
        }
        
        if auth_type == "Basic":
            broker_props["solace.messaging.authentication.scheme.basic.username"] = username
            broker_props["solace.messaging.authentication.scheme.basic.password"] = password
        
        messaging_service = MessagingService.builder().from_properties(broker_props)\
            .with_reconnection_retry_strategy(RetryStrategy.parametrized_retry(0, 1))\
            .build()
        
        messaging_service.connect()
        
        if messaging_service.is_connected:
            messaging_service.disconnect()
            return True, f"Successfully authenticated to Solace broker at {host}:{port} (VPN: {vpn})"
        else:
            return False, "Connection established but not authenticated"
            
    except ImportError:
        # Fall back to TCP connection test
        pass
    except Exception as e:
        return False, f"Solace authentication failed: {e}"
    
    # Fallback: basic TCP/TLS connection test
    try:
        import socket
        import ssl
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        if use_tls:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            sock = context.wrap_socket(sock, server_hostname=host)
        
        sock.connect((host, int(port)))
        sock.close()
        
        return True, f"TCP{'S' if use_tls else ''} connection successful to {host}:{port} (Note: solace-pubsubplus package not installed for full auth test)"
        
    except Exception as e:
        return False, f"Connection failed: {e}"
