"""ONVIF authentication module."""

module_description = "ONVIF (Video)"

form_fields = [
    {"name": "host", "type": "text", "label": "Camera Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "80",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 443, Non-TLS: 80. ONVIF standard. admin / admin."}
]

def authenticate(form_data):
    """Test ONVIF authentication."""
    try:
        host = form_data.get("host", "")
        port = form_data.get("port", "80")
        username = form_data.get("username", "admin")
        password = form_data.get("password", "")
        use_https = form_data.get("use_https", False)
        
        try:
            from onvif import ONVIFCamera
            
            cam = ONVIFCamera(host, int(port), username, password)
            device_info = cam.devicemgmt.GetDeviceInformation()
            
            return True, f"ONVIF authentication successful ({device_info.Manufacturer} {device_info.Model})"
            
        except ImportError:
            # Fallback to SOAP request
            import requests
            from requests.auth import HTTPDigestAuth
            
            protocol = "https" if use_https else "http"
            base_url = f"{protocol}://{host}:{port}"
            
            # ONVIF GetDeviceInformation SOAP request
            soap_body = """<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" 
                           xmlns:tds="http://www.onvif.org/ver10/device/wsdl">
                <soap:Body>
                    <tds:GetDeviceInformation/>
                </soap:Body>
            </soap:Envelope>"""
            
            response = requests.post(
                f"{base_url}/onvif/device_service",
                data=soap_body,
                headers={"Content-Type": "application/soap+xml"},
                auth=HTTPDigestAuth(username, password),
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200 and "GetDeviceInformationResponse" in response.text:
                return True, "ONVIF authentication successful"
            elif response.status_code == 401:
                return False, "Authentication failed"
            else:
                return False, f"HTTP {response.status_code}"
                
    except Exception as e:
        return False, f"ONVIF error: {str(e)}"

