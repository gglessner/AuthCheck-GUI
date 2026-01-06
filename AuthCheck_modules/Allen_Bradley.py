"""Allen-Bradley/Rockwell PLC authentication module."""

module_description = "Allen-Bradley / Rockwell PLC (ICS)"

form_fields = [
    {"name": "host", "type": "text", "label": "PLC Host", "default": "192.168.0.1"},
    {"name": "port", "type": "text", "label": "Port", "default": "44818"},
    {"name": "slot", "type": "text", "label": "Slot", "default": "0"},
    {"name": "tag_name", "type": "text", "label": "Test Tag", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default port 44818. No auth by default. ControlLogix/CompactLogix."}
]

def authenticate(form_data):
    """Test Allen-Bradley connection."""
    try:
        from pylogix import PLC
        
        host = form_data.get("host", "192.168.0.1")
        slot = int(form_data.get("slot", 0))
        tag_name = form_data.get("tag_name", "")
        
        with PLC() as comm:
            comm.IPAddress = host
            comm.ProcessorSlot = slot
            
            # Get PLC time to verify connection
            ret = comm.GetPLCTime()
            
            if ret.Status == "Success":
                return True, f"Allen-Bradley connection successful to {host} (Slot {slot})"
            else:
                return False, f"Connection failed: {ret.Status}"
        
    except ImportError:
        return False, "pylogix library not installed. Install with: pip install pylogix"
    except Exception as e:
        return False, f"Allen-Bradley error: {str(e)}"

