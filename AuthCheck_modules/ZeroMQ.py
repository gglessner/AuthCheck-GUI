# ZeroMQ Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "ZeroMQ (MQ)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "5555"},
    {"name": "socket_type", "type": "combo", "label": "Socket Type",
     "options": ["REQ/REP", "PUB/SUB", "PUSH/PULL", "DEALER/ROUTER"]},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Plain", "Curve"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "server_key", "type": "text", "label": "Server Public Key (Curve)"},
    {"name": "client_public", "type": "text", "label": "Client Public Key (Curve)"},
    {"name": "client_secret", "type": "password", "label": "Client Secret Key (Curve)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default port: 5555. Auth types: None, Plain, Curve (Z85 keys)"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to ZeroMQ.
    """
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    socket_type = form_data.get('socket_type', 'REQ/REP')
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    server_key = form_data.get('server_key', '').strip()
    client_public = form_data.get('client_public', '').strip()
    client_secret = form_data.get('client_secret', '').strip()
    
    if not host:
        return False, "Host is required"
    if not port:
        return False, "Port is required"
    
    try:
        import zmq
    except ImportError:
        return False, "pyzmq package not installed. Run: pip install pyzmq"
    
    try:
        context = zmq.Context()
        
        if "REQ" in socket_type:
            socket = context.socket(zmq.REQ)
        elif "SUB" in socket_type:
            socket = context.socket(zmq.SUB)
            socket.setsockopt_string(zmq.SUBSCRIBE, "")
        elif "PULL" in socket_type:
            socket = context.socket(zmq.PULL)
        elif "DEALER" in socket_type:
            socket = context.socket(zmq.DEALER)
        else:
            socket = context.socket(zmq.REQ)
        
        socket.setsockopt(zmq.LINGER, 0)
        socket.setsockopt(zmq.RCVTIMEO, 5000)
        socket.setsockopt(zmq.SNDTIMEO, 5000)
        
        if auth_type == "Plain":
            socket.plain_username = username.encode() if username else b""
            socket.plain_password = password.encode() if password else b""
        elif auth_type == "Curve":
            if server_key and client_public and client_secret:
                socket.curve_serverkey = server_key.encode()
                socket.curve_publickey = client_public.encode()
                socket.curve_secretkey = client_secret.encode()
        
        endpoint = f"tcp://{host}:{port}"
        socket.connect(endpoint)
        
        if "REQ" in socket_type or "DEALER" in socket_type:
            socket.send(b"PING")
            try:
                response = socket.recv()
                socket.close()
                context.term()
                return True, f"Successfully connected to ZeroMQ at {endpoint}\nResponse: {response.decode('utf-8', errors='ignore')[:50]}"
            except zmq.Again:
                socket.close()
                context.term()
                return True, f"Connected to ZeroMQ at {endpoint} (no response within timeout)"
        else:
            try:
                msg = socket.recv()
                socket.close()
                context.term()
                return True, f"Successfully connected to ZeroMQ at {endpoint}\nReceived: {len(msg)} bytes"
            except zmq.Again:
                socket.close()
                context.term()
                return True, f"Connected to ZeroMQ at {endpoint} (no messages within timeout)"
        
    except zmq.ZMQError as e:
        if "authentication" in str(e).lower():
            return False, f"Authentication failed: {e}"
        return False, f"ZeroMQ error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

