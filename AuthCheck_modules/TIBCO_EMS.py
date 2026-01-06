# TIBCO EMS Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "TIBCO EMS (MQ)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "7222",
     "port_toggle": "use_ssl", "tls_port": "7243", "non_tls_port": "7222"},
    {"name": "use_ssl", "type": "checkbox", "label": "Enable SSL"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 7243, Non-TLS: 7222. admin / admin"},
]


def authenticate(form_data):
    """Attempt to authenticate to TIBCO EMS via STOMP."""
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '7222').strip()
    use_ssl = form_data.get('use_ssl', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    if not host:
        return False, "Host is required"
    
    # Try STOMP connection (EMS supports STOMP)
    try:
        import stomp
    except ImportError:
        # Fall back to TCP test
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, int(port)))
            sock.close()
            return True, f"TCP connection to TIBCO EMS at {host}:{port} successful\n(stomp.py not installed for full auth check)"
        except Exception as e:
            return False, f"Connection failed: {e}"
    
    try:
        port_num = int(port) if port else 7222
        conn = stomp.Connection([(host, port_num)])
        
        if use_ssl:
            conn.set_ssl([(host, port_num)])
        
        conn.connect(username, password, wait=True)
        
        if conn.is_connected():
            conn.disconnect()
            return True, f"Successfully authenticated to TIBCO EMS at {host}:{port_num}"
        else:
            return False, "Connection failed"
            
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "login" in error_msg.lower():
            return False, f"Authentication failed: {e}"
        return False, f"TIBCO EMS error: {e}"

