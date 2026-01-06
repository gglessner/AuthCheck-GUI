"""LwM2M (Lightweight M2M) authentication module."""

module_description = "LwM2M (IoT)"

form_fields = [
    {"name": "host", "type": "text", "label": "LwM2M Server", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "5683"},
    {"name": "endpoint_name", "type": "text", "label": "Endpoint Name", "default": "test-device"},
    {"name": "use_dtls", "type": "checkbox", "label": "Use DTLS", "default": False},
    {"name": "psk_identity", "type": "text", "label": "PSK Identity", "default": ""},
    {"name": "psk_key", "type": "password", "label": "PSK Key (hex)", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "CoAP port 5683, DTLS port 5684. Bootstrap server for provisioning."}
]

def authenticate(form_data):
    """Test LwM2M server connectivity."""
    try:
        import socket
        
        host = form_data.get("host", "localhost")
        port = int(form_data.get("port", 5683))
        use_dtls = form_data.get("use_dtls", False)
        
        # LwM2M uses CoAP - test basic UDP connectivity
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(10)
        
        # Simple CoAP header (Version 1, Type Confirmable, Token length 0)
        # GET request to /.well-known/core
        coap_request = bytes([0x40, 0x01, 0x00, 0x01, 0xbb, 0x2e, 0x77, 0x65, 0x6c, 0x6c, 0x2d, 0x6b, 0x6e, 0x6f, 0x77, 0x6e, 0x04, 0x63, 0x6f, 0x72, 0x65])
        
        sock.sendto(coap_request, (host, port))
        
        try:
            data, addr = sock.recvfrom(1024)
            sock.close()
            return True, f"LwM2M/CoAP server responding at {host}:{port}"
        except socket.timeout:
            sock.close()
            return False, f"No response from {host}:{port}"
            
    except Exception as e:
        return False, f"LwM2M error: {str(e)}"

