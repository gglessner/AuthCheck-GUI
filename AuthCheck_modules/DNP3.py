"""DNP3 authentication module."""

module_description = "DNP3 (ICS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "20000",
     "port_toggle": "use_tls", "tls_port": "20001", "non_tls_port": "20000"},
    {"name": "master_address", "type": "text", "label": "Master Address", "default": "1"},
    {"name": "outstation_address", "type": "text", "label": "Outstation Address", "default": "10"},
    {"name": "use_tls", "type": "checkbox", "label": "Use TLS", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 20001, Non-TLS: 20000. Secure Auth: challenge-response. Master=1, Outstation=10"}
]

def authenticate(form_data):
    """Test DNP3 connection."""
    try:
        from pydnp3 import opendnp3, openpal, asiopal, asiodnp3
        
        host = form_data.get("host", "localhost")
        port = int(form_data.get("port", 20000))
        
        # DNP3 requires more complex setup
        return False, "DNP3 authentication check requires full protocol stack. Use dedicated SCADA tools."
        
    except ImportError:
        # Fallback to TCP connection test
        import socket
        
        host = form_data.get("host", "localhost")
        port = int(form_data.get("port", 20000))
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, port))
            sock.close()
            return True, f"TCP connection to DNP3 port {host}:{port} successful (protocol auth not tested)"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    except Exception as e:
        return False, f"DNP3 error: {str(e)}"

