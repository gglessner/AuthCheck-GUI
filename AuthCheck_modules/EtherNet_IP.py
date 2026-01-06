"""EtherNet/IP authentication module."""

module_description = "EtherNet/IP (ICS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.0.1"},
    {"name": "port", "type": "text", "label": "Port", "default": "44818"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "CIP over Ethernet. Default port 44818. No authentication standard."}
]

def authenticate(form_data):
    """Test EtherNet/IP connection."""
    try:
        from cpppo.server.enip import client
        
        host = form_data.get("host", "192.168.0.1")
        port = int(form_data.get("port", 44818))
        
        with client.connector(host=host, port=port) as conn:
            # Try to list services
            conn.list_services()
            return True, f"EtherNet/IP connection successful to {host}:{port}"
        
    except ImportError:
        # Fallback to TCP test
        import socket
        host = form_data.get("host", "192.168.0.1")
        port = int(form_data.get("port", 44818))
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, port))
            sock.close()
            return True, f"TCP connection to EtherNet/IP port successful (protocol not tested)"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    except Exception as e:
        return False, f"EtherNet/IP error: {str(e)}"

