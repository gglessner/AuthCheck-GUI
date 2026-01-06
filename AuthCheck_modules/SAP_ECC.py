"""SAP ECC authentication module."""

module_description = "SAP ECC (ERP)"

form_fields = [
    {"name": "host", "type": "text", "label": "SAP Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "client", "type": "text", "label": "Client", "default": "100"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "SAP ECC 6.0. RFC/BAPI or web services. Default client 000/100."}
]

def authenticate(form_data):
    """Test SAP ECC authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        client = form_data.get("client", "100")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}"
        
        # Try web service ping
        response = requests.get(
            f"{base_url}/sap/bc/ping",
            auth=HTTPBasicAuth(username, password),
            params={"sap-client": client},
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "SAP ECC authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"SAP ECC error: {str(e)}"

