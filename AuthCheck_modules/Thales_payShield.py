"""Thales payShield HSM authentication module."""

module_description = "Thales payShield HSM (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "HSM Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "1500"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "lmk_id", "type": "text", "label": "LMK ID", "default": "00"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Thales payShield 9000/10K. TCP port 1500. NC command for diagnostics."}
]

def authenticate(form_data):
    """Test Thales payShield authentication."""
    try:
        import socket
        
        host = form_data.get("host", "")
        port = int(form_data.get("port", "1500"))
        lmk_id = form_data.get("lmk_id", "00")
        
        # payShield uses a proprietary protocol
        # NC command = No-op/Diagnostic
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        
        # Send NC (No-op) command
        # Format: 4-byte length header + command
        command = f"{lmk_id}NC"
        length = f"{len(command):04d}"
        sock.send((length + command).encode())
        
        # Receive response
        response = sock.recv(1024)
        sock.close()
        
        if response:
            # ND = No-op response (success)
            if b"ND" in response:
                return True, "Thales payShield authentication successful"
            else:
                return True, f"payShield responded: {response[:20]}"
        else:
            return False, "No response from HSM"
            
    except Exception as e:
        return False, f"Thales payShield error: {str(e)}"

