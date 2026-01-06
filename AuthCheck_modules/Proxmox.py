"""Proxmox VE authentication module."""

module_description = "Proxmox VE (Virtualization)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8006",
     "port_toggle": "verify_ssl", "tls_port": "8006", "non_tls_port": "8006"},
    {"name": "username", "type": "text", "label": "Username", "default": "root@pam"},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "realm", "type": "combo", "label": "Realm", "options": ["pam", "pve", "ldap", "ad"], "default": "pam"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 8006 (TLS default). root@pam. Token: user@realm!tokenid"}
]

def authenticate(form_data):
    """Test Proxmox authentication."""
    try:
        from proxmoxer import ProxmoxAPI
        
        host = form_data.get("host", "localhost")
        port = int(form_data.get("port", 8006))
        username = form_data.get("username", "root@pam")
        password = form_data.get("password", "")
        verify_ssl = form_data.get("verify_ssl", False)
        
        # Parse username if realm not included
        if "@" not in username:
            realm = form_data.get("realm", "pam")
            username = f"{username}@{realm}"
        
        proxmox = ProxmoxAPI(
            host,
            port=port,
            user=username,
            password=password,
            verify_ssl=verify_ssl
        )
        
        # Test by getting version
        version = proxmox.version.get()
        return True, f"Proxmox authentication successful (v{version.get('version', 'unknown')})"
        
    except ImportError:
        return False, "proxmoxer library not installed. Install with: pip install proxmoxer"
    except Exception as e:
        return False, f"Proxmox error: {str(e)}"

