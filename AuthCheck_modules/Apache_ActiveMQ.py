# Apache ActiveMQ Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache ActiveMQ (MQ)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "web_port", "type": "text", "label": "Web Console Port", "default": "8161",
     "port_toggle": "use_ssl", "tls_port": "8162", "non_tls_port": "8161"},
    {"name": "openwire_port", "type": "text", "label": "OpenWire Port", "default": "61616",
     "port_toggle": "use_ssl", "tls_port": "61617", "non_tls_port": "61616"},
    {"name": "stomp_port", "type": "text", "label": "STOMP Port", "default": "61613",
     "port_toggle": "use_ssl", "tls_port": "61614", "non_tls_port": "61613"},
    {"name": "amqp_port", "type": "text", "label": "AMQP Port", "default": "5672",
     "port_toggle": "use_ssl", "tls_port": "5671", "non_tls_port": "5672"},
    {"name": "protocol", "type": "combo", "label": "Protocol",
     "options": ["Web Console/Jolokia", "OpenWire", "STOMP", "AMQP"]},
    {"name": "use_ssl", "type": "checkbox", "label": "Enable SSL/TLS"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "OpenWire: 61616/61617, STOMP: 61613/61614, AMQP: 5672/5671. admin / admin"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache ActiveMQ.
    """
    host = form_data.get('host', '').strip()
    web_port = form_data.get('web_port', '8161').strip()
    openwire_port = form_data.get('openwire_port', '61616').strip()
    stomp_port = form_data.get('stomp_port', '61613').strip()
    amqp_port = form_data.get('amqp_port', '5672').strip()
    protocol = form_data.get('protocol', 'Web Console/Jolokia')
    use_ssl = form_data.get('use_ssl', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    if protocol == "OpenWire":
        # OpenWire is ActiveMQ's native binary protocol
        # We'll test using socket connection and protocol handshake
        try:
            import socket
            import ssl as ssl_module
        except ImportError:
            return False, "socket/ssl modules not available"
        
        try:
            port = int(openwire_port) if openwire_port else 61616
            
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            if use_ssl:
                context = ssl_module.create_default_context()
                if not verify_ssl:
                    context.check_hostname = False
                    context.verify_mode = ssl_module.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=host)
            
            sock.connect((host, port))
            
            # OpenWire protocol magic bytes for WIREFORMAT_INFO command
            # This is the initial handshake - if we can connect, the port is active
            # Full OpenWire auth requires JMS client, but we can verify connectivity
            
            # Send a minimal probe - ActiveMQ will respond or close
            # OpenWire starts with a WIREFORMAT_INFO frame
            wireformat_probe = bytes([
                0x00, 0x00, 0x00, 0x00,  # Length placeholder
                0x01,  # WIREFORMAT_INFO type
            ])
            
            try:
                sock.send(wireformat_probe)
                response = sock.recv(1024)
                sock.close()
                
                if response:
                    # Got a response - OpenWire port is active
                    # For full auth verification, use Web Console with same credentials
                    return True, f"OpenWire port {port} is active on {host}\nNote: Full credential verification uses Web Console API"
                else:
                    return False, f"No response from OpenWire port {port}"
            except Exception as e:
                sock.close()
                # Connection accepted means port is listening
                return True, f"OpenWire port {port} accepting connections on {host}\nConnection test: {e}"
                
        except socket.timeout:
            return False, f"Connection timeout to {host}:{port}"
        except ConnectionRefusedError:
            return False, f"Connection refused to {host}:{port} - OpenWire not listening"
        except Exception as e:
            return False, f"OpenWire connection error: {e}"
    
    elif protocol == "Web Console/Jolokia":
        # Use Jolokia REST API for authentication verification
        try:
            import requests
            from requests.auth import HTTPBasicAuth
        except ImportError:
            return False, "requests package not installed. Run: pip install requests"
        
        try:
            scheme = "https" if use_ssl else "http"
            port = web_port if web_port else "8161"
            
            # Try Jolokia API endpoint
            jolokia_url = f"{scheme}://{host}:{port}/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=*"
            
            auth = HTTPBasicAuth(username, password) if username else None
            response = requests.get(jolokia_url, auth=auth, verify=verify_ssl, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 200:
                    # Extract broker info
                    value = data.get('value', {})
                    broker_info = list(value.values())[0] if value else {}
                    broker_name = broker_info.get('BrokerName', 'unknown')
                    broker_version = broker_info.get('BrokerVersion', 'unknown')
                    queues = broker_info.get('Queues', [])
                    topics = broker_info.get('Topics', [])
                    
                    return True, f"Successfully authenticated to Apache ActiveMQ {broker_version}\nBroker: {broker_name}\nQueues: {len(queues)}, Topics: {len(topics)}"
                else:
                    return False, f"Jolokia error: {data.get('error', 'Unknown error')}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            elif response.status_code == 403:
                return False, "Authentication failed: Forbidden"
            else:
                # Fallback to legacy web console API
                legacy_url = f"{scheme}://{host}:{port}/admin/queues.jsp"
                legacy_response = requests.get(legacy_url, auth=auth, verify=verify_ssl, timeout=10)
                if legacy_response.status_code == 200:
                    return True, f"Successfully authenticated to Apache ActiveMQ at {host}:{port}"
                return False, f"HTTP {response.status_code}: {response.text[:200]}"
                
        except Exception as e:
            return False, f"ActiveMQ Web Console error: {e}"
    
    elif protocol == "STOMP":
        try:
            import stomp
        except ImportError:
            return False, "stomp.py package not installed. Run: pip install stomp.py"
        
        try:
            port = int(stomp_port) if stomp_port else 61613
            conn = stomp.Connection([(host, port)])
            
            if use_ssl:
                conn.set_ssl([(host, port)])
            
            conn.connect(username, password, wait=True)
            
            if conn.is_connected():
                conn.disconnect()
                return True, f"Successfully authenticated to ActiveMQ at {host}:{port} via STOMP"
            else:
                return False, "Connection established but authentication failed"
                
        except stomp.exception.ConnectFailedException as e:
            return False, f"STOMP connection failed: {e}"
        except Exception as e:
            return False, f"STOMP error: {e}"
    
    elif protocol == "AMQP":
        try:
            import pika
        except ImportError:
            return False, "pika package not installed. Run: pip install pika"
        
        try:
            port = int(amqp_port) if amqp_port else 5672
            credentials = pika.PlainCredentials(username, password)
            
            ssl_options = None
            if use_ssl:
                import ssl
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE if not verify_ssl else ssl.CERT_REQUIRED
                ssl_options = pika.SSLOptions(context, host)
            
            parameters = pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=credentials,
                ssl_options=ssl_options,
                connection_attempts=1,
                socket_timeout=10
            )
            
            connection = pika.BlockingConnection(parameters)
            
            if connection.is_open:
                connection.close()
                return True, f"Successfully authenticated to ActiveMQ at {host}:{port} via AMQP"
            else:
                return False, "Connection established but not open"
                
        except pika.exceptions.AMQPConnectionError as e:
            return False, f"AMQP connection error: {e}"
        except Exception as e:
            return False, f"AMQP error: {e}"
    
    return False, f"Unknown protocol: {protocol}"
