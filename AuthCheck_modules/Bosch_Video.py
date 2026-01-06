"""Bosch Video authentication module."""

module_description = "Bosch Video (Video)"

form_fields = [
    {"name": "host", "type": "text", "label": "Camera/BVMS Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "80",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "username", "type": "text", "label": "Username", "default": "service"},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 443, Non-TLS: 80. service / (blank), live / (blank)."}
]

def authenticate(form_data):
    """Test Bosch Video authentication."""
    try:
        import requests
        from requests.auth import HTTPDigestAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "80")
        username = form_data.get("username", "service")
        password = form_data.get("password", "")
        use_https = form_data.get("use_https", False)
        
        protocol = "https" if use_https else "http"
        base_url = f"{protocol}://{host}:{port}"
        
        response = requests.get(
            f"{base_url}/rcp.xml?command=0x0001&type=P_OCTET&direction=READ",
            auth=HTTPDigestAuth(username, password),
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            return True, "Bosch Video authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Bosch Video error: {str(e)}"

