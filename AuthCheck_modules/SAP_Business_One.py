"""SAP Business One authentication module."""

module_description = "SAP Business One (ERP)"

form_fields = [
    {"name": "host", "type": "text", "label": "Service Layer Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "50000"},
    {"name": "company_db", "type": "text", "label": "Company Database", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "SAP Business One Service Layer. Default: manager."}
]

def authenticate(form_data):
    """Test SAP Business One authentication."""
    try:
        import requests
        
        host = form_data.get("host", "")
        port = form_data.get("port", "50000")
        company_db = form_data.get("company_db", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}/b1s/v1"
        
        session = requests.Session()
        
        response = session.post(
            f"{base_url}/Login",
            json={
                "CompanyDB": company_db,
                "UserName": username,
                "Password": password
            },
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            # Logout
            session.post(f"{base_url}/Logout", verify=verify_ssl)
            return True, "SAP Business One authentication successful"
        else:
            data = response.json()
            return False, f"Auth failed: {data.get('error', {}).get('message', {}).get('value', 'Unknown')}"
            
    except Exception as e:
        return False, f"SAP B1 error: {str(e)}"

