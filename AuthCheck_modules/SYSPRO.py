"""SYSPRO ERP authentication module."""

module_description = "SYSPRO (ERP)"

form_fields = [
    {"name": "host", "type": "text", "label": "SYSPRO Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Operator", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "company", "type": "text", "label": "Company", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "SYSPRO ERP. e.net Services or SYSPRO 8 Avanti web services."}
]

def authenticate(form_data):
    """Test SYSPRO authentication."""
    try:
        import requests
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        company = form_data.get("company", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}"
        
        response = requests.post(
            f"{base_url}/SYSPROWCFService/Rest/Logon",
            json={
                "Operator": username,
                "OperatorPassword": password,
                "Company": company,
                "CompanyPassword": ""
            },
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ErrorMessage", "") == "":
                return True, "SYSPRO authentication successful"
            else:
                return False, f"SYSPRO: {data.get('ErrorMessage')}"
        
        return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"SYSPRO error: {str(e)}"

