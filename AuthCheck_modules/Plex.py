"""Plex Media Server authentication module."""

module_description = "Plex (Media)"

form_fields = [
    {"name": "host", "type": "text", "label": "Plex Server", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "32400",
     "port_toggle": "verify_ssl", "tls_port": "32400", "non_tls_port": "32400"},
    {"name": "token", "type": "password", "label": "X-Plex-Token", "default": ""},
    {"name": "username", "type": "text", "label": "Plex Username (optional)", "default": ""},
    {"name": "password", "type": "password", "label": "Plex Password (optional)", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 32400 (TLS/non-TLS same). Token from XML/app.plex.tv."}
]

def authenticate(form_data):
    """Test Plex authentication."""
    try:
        from plexapi.server import PlexServer
        from plexapi.myplex import MyPlexAccount
        
        host = form_data.get("host", "localhost")
        port = form_data.get("port", "32400")
        token = form_data.get("token", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        
        if token:
            base_url = f"http://{host}:{port}"
            plex = PlexServer(base_url, token)
        elif username and password:
            account = MyPlexAccount(username, password)
            resources = account.resources()
            return True, f"Plex.tv auth successful ({len(resources)} resources)"
        else:
            return False, "Token or username/password required"
        
        # Test by getting library sections
        libraries = plex.library.sections()
        
        return True, f"Plex authentication successful ({len(libraries)} libraries)"
        
    except ImportError:
        return False, "plexapi library not installed. Install with: pip install plexapi"
    except Exception as e:
        return False, f"Plex error: {str(e)}"

