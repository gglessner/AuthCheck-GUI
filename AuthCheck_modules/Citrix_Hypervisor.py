"""Citrix Hypervisor (XenServer) authentication module."""

module_description = "Citrix Hypervisor / XenServer (Virtualization)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: root with host password. XAPI on port 443."}
]

def authenticate(form_data):
    """Test Citrix Hypervisor authentication."""
    try:
        import XenAPI
        
        host = form_data.get("host", "localhost")
        username = form_data.get("username", "root")
        password = form_data.get("password", "")
        
        session = XenAPI.Session(f"https://{host}")
        session.xenapi.login_with_password(username, password)
        
        # Get host info
        hosts = session.xenapi.host.get_all()
        
        session.xenapi.session.logout()
        return True, f"Citrix Hypervisor authentication successful ({len(hosts)} host(s))"
        
    except ImportError:
        return False, "XenAPI library not installed. Install with: pip install XenAPI"
    except Exception as e:
        return False, f"XenServer error: {str(e)}"

