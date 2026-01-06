"""AWS API Gateway authentication module."""

module_description = "AWS API Gateway (Cloud)"

form_fields = [
    {"name": "access_key", "type": "text", "label": "AWS Access Key ID", "default": ""},
    {"name": "secret_key", "type": "password", "label": "AWS Secret Access Key", "default": ""},
    {"name": "region", "type": "text", "label": "Region", "default": "us-east-1"},
    {"name": "api_id", "type": "text", "label": "API ID (optional)", "default": ""},
    {"name": "session_token", "type": "password", "label": "Session Token (for STS)", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Uses AWS IAM credentials. Can use env vars AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY"}
]

def authenticate(form_data):
    """Test AWS API Gateway authentication."""
    try:
        import boto3
        
        access_key = form_data.get("access_key", "")
        secret_key = form_data.get("secret_key", "")
        region = form_data.get("region", "us-east-1")
        api_id = form_data.get("api_id", "")
        session_token = form_data.get("session_token", "")
        
        session_kwargs = {"region_name": region}
        if access_key and secret_key:
            session_kwargs["aws_access_key_id"] = access_key
            session_kwargs["aws_secret_access_key"] = secret_key
            if session_token:
                session_kwargs["aws_session_token"] = session_token
        
        session = boto3.Session(**session_kwargs)
        client = session.client("apigateway")
        
        if api_id:
            api = client.get_rest_api(restApiId=api_id)
            return True, f"AWS API Gateway auth successful (API: {api.get('name')})"
        else:
            apis = client.get_rest_apis(limit=1)
            count = len(apis.get("items", []))
            return True, f"AWS API Gateway auth successful ({count}+ APIs found)"
            
    except ImportError:
        return False, "boto3 library not installed. Install with: pip install boto3"
    except Exception as e:
        return False, f"AWS API Gateway error: {str(e)}"

