"""SAP S/4HANA authentication module."""

module_description = "SAP S/4HANA (ERP)"

form_fields = [
    {"name": "host", "type": "text", "label": "S/4HANA Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "client", "type": "text", "label": "Client", "default": "100"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "SAP S/4HANA. Default client 100. DDIC for system admin."}
]

def authenticate(form_data):
    """Test SAP S/4HANA authentication."""
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
        
        response = requests.get(
            f"{base_url}/sap/opu/odata/sap/API_BUSINESS_PARTNER/A_BusinessPartner",
            auth=HTTPBasicAuth(username, password),
            params={"$top": 1, "sap-client": client},
            headers={"Accept": "application/json"},
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "SAP S/4HANA authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"SAP S/4HANA error: {str(e)}"

