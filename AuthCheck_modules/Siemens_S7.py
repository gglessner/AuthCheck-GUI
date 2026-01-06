"""Siemens S7 PLC authentication module."""

module_description = "Siemens S7 PLC (ICS)"

form_fields = [
    {"name": "host", "type": "text", "label": "PLC Host", "default": "192.168.0.1"},
    {"name": "port", "type": "text", "label": "Port", "default": "102"},
    {"name": "rack", "type": "text", "label": "Rack", "default": "0"},
    {"name": "slot", "type": "text", "label": "Slot", "default": "1"},
    {"name": "password", "type": "password", "label": "Password (if protected)", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "S7-300: Rack=0, Slot=2. S7-400: Slot=3. S7-1200/1500: Slot=1. Default no password."}
]

def authenticate(form_data):
    """Test Siemens S7 connection."""
    try:
        import snap7
        
        host = form_data.get("host", "192.168.0.1")
        rack = int(form_data.get("rack", 0))
        slot = int(form_data.get("slot", 1))
        password = form_data.get("password", "")
        
        client = snap7.client.Client()
        client.connect(host, rack, slot)
        
        if password:
            client.set_session_password(password)
        
        # Try to get CPU info
        info = client.get_cpu_info()
        
        client.disconnect()
        return True, f"S7 connection successful to {host} (Rack {rack}, Slot {slot})"
        
    except ImportError:
        return False, "snap7 library not installed. Install with: pip install python-snap7"
    except Exception as e:
        return False, f"S7 error: {str(e)}"

