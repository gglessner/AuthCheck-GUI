"""Bloomberg Terminal authentication module."""

module_description = "Bloomberg (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "Server Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8194"},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["User Mode", "Application Mode", "Server API"], "default": "User Mode"},
    {"name": "app_name", "type": "text", "label": "Application Name", "default": ""},
    {"name": "uuid", "type": "text", "label": "UUID (for Server API)", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Bloomberg API uses B-PIPE. Port 8194 default. Requires Bloomberg subscription."}
]

def authenticate(form_data):
    """Test Bloomberg API connection."""
    try:
        import blpapi
        
        host = form_data.get("host", "localhost")
        port = int(form_data.get("port", 8194))
        auth_type = form_data.get("auth_type", "User Mode")
        
        session_options = blpapi.SessionOptions()
        session_options.setServerHost(host)
        session_options.setServerPort(port)
        
        session = blpapi.Session(session_options)
        
        if session.start():
            if session.openService("//blp/refdata"):
                session.stop()
                return True, f"Bloomberg API connection successful to {host}:{port}"
            else:
                session.stop()
                return False, "Failed to open reference data service"
        else:
            return False, "Failed to start Bloomberg session"
            
    except ImportError:
        return False, "blpapi library not installed. Bloomberg SDK required."
    except Exception as e:
        return False, f"Bloomberg error: {str(e)}"

