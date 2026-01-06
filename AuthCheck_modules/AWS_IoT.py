"""AWS IoT Core authentication module."""

module_description = "AWS IoT Core (IoT)"

form_fields = [
    {"name": "endpoint", "type": "text", "label": "IoT Endpoint", "default": ""},
    {"name": "access_key", "type": "text", "label": "AWS Access Key ID", "default": ""},
    {"name": "secret_key", "type": "password", "label": "AWS Secret Access Key", "default": ""},
    {"name": "region", "type": "text", "label": "Region", "default": "us-east-1"},
    {"name": "cert_path", "type": "file", "label": "Device Certificate", "filter": "Certificate Files (*.pem *.crt)"},
    {"name": "key_path", "type": "file", "label": "Private Key", "filter": "Key Files (*.pem *.key)"},
    {"name": "ca_cert", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Endpoint: xxx.iot.region.amazonaws.com. Uses X.509 certs or IAM."}
]

def authenticate(form_data):
    """Test AWS IoT authentication."""
    try:
        import boto3
        
        access_key = form_data.get("access_key", "")
        secret_key = form_data.get("secret_key", "")
        region = form_data.get("region", "us-east-1")
        
        session_kwargs = {"region_name": region}
        if access_key and secret_key:
            session_kwargs["aws_access_key_id"] = access_key
            session_kwargs["aws_secret_access_key"] = secret_key
        
        session = boto3.Session(**session_kwargs)
        client = session.client("iot")
        
        # List things to verify access
        things = client.list_things(maxResults=1)
        
        return True, f"AWS IoT authentication successful"
        
    except ImportError:
        return False, "boto3 library not installed. Install with: pip install boto3"
    except Exception as e:
        return False, f"AWS IoT error: {str(e)}"

