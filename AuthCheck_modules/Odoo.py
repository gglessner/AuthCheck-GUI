"""Odoo ERP authentication module."""

module_description = "Odoo (ERP)"

form_fields = [
    {"name": "host", "type": "text", "label": "Odoo Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "database", "type": "text", "label": "Database", "default": ""},
    {"name": "username", "type": "text", "label": "Username/Email", "default": ""},
    {"name": "password", "type": "password", "label": "Password/API Key", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Odoo. Default admin: admin@example.com. XML-RPC or JSON-RPC."}
]

def authenticate(form_data):
    """Test Odoo authentication."""
    try:
        import xmlrpc.client
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        database = form_data.get("database", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        
        url = f"https://{host}:{port}"
        
        # Common endpoint for authentication
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        
        uid = common.authenticate(database, username, password, {})
        
        if uid:
            return True, f"Odoo authentication successful (UID: {uid})"
        else:
            return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Odoo error: {str(e)}"

