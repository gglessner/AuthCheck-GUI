"""IBM CICS authentication module."""

module_description = "IBM CICS (Mainframe)"

form_fields = [
    {"name": "host", "type": "text", "label": "CICS Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "1490",
     "port_toggle": "use_ssl", "tls_port": "1491", "non_tls_port": "1490"},
    {"name": "userid", "type": "text", "label": "User ID", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "applid", "type": "text", "label": "CICS APPLID", "default": ""},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 1491, Non-TLS: 1490. CICS TS. RACF/ACF2/TSS auth."}
]

def authenticate(form_data):
    """Test CICS authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "1490")
        userid = form_data.get("userid", "")
        password = form_data.get("password", "")
        use_ssl = form_data.get("use_ssl", True)
        
        protocol = "https" if use_ssl else "http"
        base_url = f"{protocol}://{host}:{port}"
        
        # Try CICS Web Services or CICS TS web interface
        response = requests.get(
            f"{base_url}/CICSSystemManagement",
            auth=HTTPBasicAuth(userid, password),
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"CICS authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"CICS error: {str(e)}"

