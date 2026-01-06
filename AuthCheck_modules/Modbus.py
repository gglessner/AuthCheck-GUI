"""Modbus TCP/RTU authentication module."""

module_description = "Modbus TCP/RTU (ICS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "502",
     "port_toggle": "use_tls", "tls_port": "802", "non_tls_port": "502"},
    {"name": "unit_id", "type": "text", "label": "Unit ID", "default": "1"},
    {"name": "use_tls", "type": "checkbox", "label": "Use TLS", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 802, Non-TLS: 502. No auth by default. Unit ID 1-247."}
]

def authenticate(form_data):
    """Test Modbus connection."""
    try:
        from pymodbus.client import ModbusTcpClient
        
        host = form_data.get("host", "localhost")
        port = int(form_data.get("port", 502))
        unit_id = int(form_data.get("unit_id", 1))
        
        client = ModbusTcpClient(host, port=port)
        
        if client.connect():
            # Try to read holding registers
            result = client.read_holding_registers(0, 1, slave=unit_id)
            client.close()
            
            if not result.isError():
                return True, f"Modbus connection successful to {host}:{port} (Unit {unit_id})"
            else:
                return True, f"Connected but read failed: {result}"
        else:
            return False, f"Failed to connect to {host}:{port}"
            
    except ImportError:
        return False, "pymodbus library not installed. Install with: pip install pymodbus"
    except Exception as e:
        return False, f"Modbus error: {str(e)}"

