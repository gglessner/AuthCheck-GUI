"""TigerGraph authentication module."""

module_description = "TigerGraph (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "REST Port", "default": "9000",
     "port_toggle": "use_ssl", "tls_port": "443", "non_tls_port": "9000"},
    {"name": "graph_name", "type": "text", "label": "Graph Name", "default": "MyGraph"},
    {"name": "username", "type": "text", "label": "Username", "default": "tigergraph"},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "secret", "type": "password", "label": "Secret (for token)", "default": ""},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 443, Non-TLS: 9000. tigergraph / tigergraph. GraphStudio 14240."}
]

def authenticate(form_data):
    """Test TigerGraph authentication."""
    try:
        import pyTigerGraph as tg
        
        host = form_data.get("host", "localhost")
        port = form_data.get("port", "9000")
        graph_name = form_data.get("graph_name", "MyGraph")
        username = form_data.get("username", "tigergraph")
        password = form_data.get("password", "")
        secret = form_data.get("secret", "")
        use_ssl = form_data.get("use_ssl", False)
        
        protocol = "https" if use_ssl else "http"
        
        conn = tg.TigerGraphConnection(
            host=f"{protocol}://{host}",
            restppPort=port,
            graphname=graph_name,
            username=username,
            password=password
        )
        
        if secret:
            conn.getToken(secret)
        
        # Test connection
        version = conn.getVer()
        
        return True, f"TigerGraph authentication successful (v{version})"
        
    except ImportError:
        return False, "pyTigerGraph library not installed. Install with: pip install pyTigerGraph"
    except Exception as e:
        return False, f"TigerGraph error: {str(e)}"

