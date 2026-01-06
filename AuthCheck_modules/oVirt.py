"""oVirt/RHEV authentication module."""

module_description = "oVirt/RHEV (Virtualization)"

form_fields = [
    {"name": "url", "type": "text", "label": "Engine URL", "default": "https://engine.example.com/ovirt-engine/api"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin@internal"},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: admin@internal. oVirt Engine API on port 443."}
]

def authenticate(form_data):
    """Test oVirt authentication."""
    try:
        import ovirtsdk4 as sdk
        
        url = form_data.get("url", "")
        username = form_data.get("username", "admin@internal")
        password = form_data.get("password", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        connection = sdk.Connection(
            url=url,
            username=username,
            password=password,
            insecure=not verify_ssl
        )
        
        api = connection.system_service().get()
        connection.close()
        
        return True, f"oVirt authentication successful (Product: {api.product_info.name})"
        
    except ImportError:
        return False, "ovirt-engine-sdk-python not installed. Install with: pip install ovirt-engine-sdk-python"
    except Exception as e:
        return False, f"oVirt error: {str(e)}"

