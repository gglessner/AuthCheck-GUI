"""Worldpay/FIS authentication module."""

module_description = "Worldpay (Payment)"

form_fields = [
    {"name": "host", "type": "text", "label": "API Host", "default": "api.worldpay.com"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "merchant_code", "type": "text", "label": "Merchant Code", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["test", "production"], "default": "test"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Worldpay (FIS) payment gateway. XML-based API."}
]

def authenticate(form_data):
    """Test Worldpay authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "api.worldpay.com")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        merchant_code = form_data.get("merchant_code", "")
        
        # Test with basic XML inquiry
        xml_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE paymentService PUBLIC "-//Worldpay//DTD Worldpay PaymentService v1//EN" "http://dtd.worldpay.com/paymentService_v1.dtd">
<paymentService version="1.4" merchantCode="{merchant_code}">
    <inquiry>
        <orderInquiry orderCode="TEST"/>
    </inquiry>
</paymentService>"""
        
        response = requests.post(
            f"https://{host}/jsp/merchant/xml/paymentService.jsp",
            data=xml_request,
            auth=HTTPBasicAuth(username, password),
            headers={"Content-Type": "application/xml"},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Worldpay authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Worldpay error: {str(e)}"

