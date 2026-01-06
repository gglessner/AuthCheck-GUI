"""AWS Greengrass authentication module."""

module_description = "AWS Greengrass (Cloud)"

form_fields = [
    {"name": "access_key", "type": "text", "label": "AWS Access Key ID", "default": ""},
    {"name": "secret_key", "type": "password", "label": "AWS Secret Access Key", "default": ""},
    {"name": "region", "type": "text", "label": "Region", "default": "us-east-1"},
    {"name": "group_id", "type": "text", "label": "Greengrass Group ID", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Uses AWS IAM credentials. Group ID from Greengrass console."}
]

def authenticate(form_data):
    """Test AWS Greengrass authentication."""
    try:
        import boto3
        
        access_key = form_data.get("access_key", "")
        secret_key = form_data.get("secret_key", "")
        region = form_data.get("region", "us-east-1")
        group_id = form_data.get("group_id", "")
        
        session_kwargs = {"region_name": region}
        if access_key and secret_key:
            session_kwargs["aws_access_key_id"] = access_key
            session_kwargs["aws_secret_access_key"] = secret_key
        
        session = boto3.Session(**session_kwargs)
        client = session.client("greengrass")
        
        if group_id:
            group = client.get_group(GroupId=group_id)
            return True, f"AWS Greengrass auth successful (Group: {group.get('Name')})"
        else:
            groups = client.list_groups(MaxResults=1)
            return True, f"AWS Greengrass auth successful ({len(groups.get('Groups', []))}+ groups)"
            
    except ImportError:
        return False, "boto3 library not installed. Install with: pip install boto3"
    except Exception as e:
        return False, f"AWS Greengrass error: {str(e)}"

