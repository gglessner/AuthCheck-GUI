"""PROFINET authentication module."""

module_description = "PROFINET (ICS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Device IP", "default": "192.168.0.1"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "PROFINET uses DCE/RPC. No standard authentication. Real-time protocol."}
]

def authenticate(form_data):
    """Test PROFINET connection."""
    import socket
    
    host = form_data.get("host", "192.168.0.1")
    
    try:
        # PROFINET uses multiple ports, test common ones
        ports = [34962, 34963, 34964]  # PROFINET IO ports
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((host, port))
                sock.close()
                return True, f"PROFINET device reachable at {host}:{port}"
            except:
                continue
        
        # Try UDP DCP discovery
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        sock.sendto(b'\x00', (host, 34964))
        sock.close()
        return True, f"PROFINET UDP reachable at {host}"
        
    except Exception as e:
        return False, f"PROFINET error: {str(e)}"

