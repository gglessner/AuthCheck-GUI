"""IBM IMS authentication module."""

module_description = "IBM IMS (Mainframe)"

form_fields = [
    {"name": "host", "type": "text", "label": "IMS Connect Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "9999",
     "port_toggle": "use_ssl", "tls_port": "9999", "non_tls_port": "9999"},
    {"name": "userid", "type": "text", "label": "User ID", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "datastorename", "type": "text", "label": "Datastore Name", "default": ""},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 9999 (TLS/non-TLS same). IMS Connect. RACF auth."}
]

def authenticate(form_data):
    """Test IMS Connect authentication."""
    try:
        import socket
        import ssl
        
        host = form_data.get("host", "")
        port = int(form_data.get("port", 9999))
        userid = form_data.get("userid", "")
        password = form_data.get("password", "")
        use_ssl = form_data.get("use_ssl", True)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        
        if use_ssl:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            sock = context.wrap_socket(sock, server_hostname=host)
        
        sock.connect((host, port))
        sock.close()
        
        return True, f"IMS Connect reachable at {host}:{port} (full auth requires IMS client)"
        
    except Exception as e:
        return False, f"IMS error: {str(e)}"

