"""IBM VTAM/SNA authentication module."""

module_description = "IBM VTAM/SNA (Mainframe)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "23",
     "port_toggle": "use_ssl", "tls_port": "992", "non_tls_port": "23"},
    {"name": "lu_name", "type": "text", "label": "LU Name", "default": ""},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 992, Non-TLS: 23. VTAM LU via TN3270/SNA gateway."}
]

def authenticate(form_data):
    """Test VTAM connectivity."""
    try:
        import socket
        import ssl
        
        host = form_data.get("host", "")
        port = int(form_data.get("port", 23))
        use_ssl = form_data.get("use_ssl", False)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        
        if use_ssl:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            sock = context.wrap_socket(sock, server_hostname=host)
        
        sock.connect((host, port))
        
        # TN3270 negotiation
        data = sock.recv(1024)
        sock.close()
        
        if data:
            return True, f"VTAM/TN3270 connection established to {host}:{port}"
        else:
            return False, "No response from host"
            
    except Exception as e:
        return False, f"VTAM error: {str(e)}"

