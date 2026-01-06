"""Sage ERP authentication module."""

module_description = "Sage (ERP)"

form_fields = [
    {"name": "host", "type": "text", "label": "Sage Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["Intacct", "X3", "100", "300", "Business Cloud"], "default": "Intacct"},
    {"name": "company_id", "type": "text", "label": "Company ID", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Sage products. Intacct uses Web Services, X3 uses REST API."}
]

def authenticate(form_data):
    """Test Sage authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        product = form_data.get("product", "Intacct")
        company_id = form_data.get("company_id", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}"
        
        if product == "Intacct":
            # Sage Intacct uses XML API
            xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
            <request>
                <control>
                    <senderid>{username}</senderid>
                    <password>{password}</password>
                    <controlid>auth_test</controlid>
                </control>
                <operation>
                    <authentication>
                        <sessionid>test</sessionid>
                    </authentication>
                </operation>
            </request>"""
            
            response = requests.post(
                "https://api.intacct.com/ia/xml/xmlgw.phtml",
                data=xml_payload,
                headers={"Content-Type": "application/xml"},
                verify=verify_ssl,
                timeout=30
            )
        else:
            response = requests.get(
                f"{base_url}/api/v1/health",
                auth=HTTPBasicAuth(username, password),
                verify=verify_ssl,
                timeout=30
            )
        
        if response.status_code == 200:
            return True, f"Sage {product} authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Sage error: {str(e)}"

