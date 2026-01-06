"""FIX Protocol authentication module."""

module_description = "FIX Protocol (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "9878",
     "port_toggle": "use_ssl", "tls_port": "9879", "non_tls_port": "9878"},
    {"name": "sender_comp_id", "type": "text", "label": "SenderCompID", "default": "CLIENT"},
    {"name": "target_comp_id", "type": "text", "label": "TargetCompID", "default": "SERVER"},
    {"name": "username", "type": "text", "label": "Username (Tag 553)", "default": ""},
    {"name": "password", "type": "password", "label": "Password (Tag 554)", "default": ""},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 9879, Non-TLS: 9878. FIX 4.2-5.0. CompIDs per server config."}
]

def authenticate(form_data):
    """Test FIX Protocol logon."""
    try:
        import socket
        import ssl
        import time
        
        host = form_data.get("host", "localhost")
        port = int(form_data.get("port", 9878))
        sender = form_data.get("sender_comp_id", "CLIENT")
        target = form_data.get("target_comp_id", "SERVER")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        use_ssl = form_data.get("use_ssl", False)
        
        # Build FIX Logon message (MsgType=A)
        seq_num = 1
        sending_time = time.strftime("%Y%m%d-%H:%M:%S")
        
        body = f"35=A\x0149={sender}\x0156={target}\x0134={seq_num}\x0152={sending_time}\x0198=0\x01108=30\x01"
        
        if username:
            body += f"553={username}\x01"
        if password:
            body += f"554={password}\x01"
        
        # Calculate checksum
        header = f"8=FIX.4.4\x019={len(body)}\x01"
        full_msg = header + body
        checksum = sum(ord(c) for c in full_msg) % 256
        message = full_msg + f"10={checksum:03d}\x01"
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        if use_ssl:
            context = ssl.create_default_context()
            sock = context.wrap_socket(sock, server_hostname=host)
        
        sock.connect((host, port))
        sock.send(message.encode())
        
        response = sock.recv(4096).decode()
        sock.close()
        
        if "35=A" in response:
            return True, f"FIX Logon successful to {host}:{port}"
        elif "35=3" in response:
            return False, f"FIX Reject received"
        elif "35=5" in response:
            return False, f"FIX Logout received"
        else:
            return False, f"Unexpected response: {response[:100]}"
            
    except Exception as e:
        return False, f"FIX error: {str(e)}"

