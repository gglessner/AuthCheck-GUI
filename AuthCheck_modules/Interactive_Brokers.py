"""Interactive Brokers authentication module."""

module_description = "Interactive Brokers (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "Gateway Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "5000"},
    {"name": "account", "type": "text", "label": "Account ID", "default": ""},
    {"name": "use_paper", "type": "checkbox", "label": "Paper Trading", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "IB Gateway or TWS. Port 5000 live, 5001 paper. Web API on 5000."}
]

def authenticate(form_data):
    """Test Interactive Brokers authentication."""
    try:
        import requests
        
        host = form_data.get("host", "localhost")
        port = form_data.get("port", "5000")
        
        base_url = f"https://{host}:{port}/v1/api"
        
        # Check authentication status
        response = requests.get(
            f"{base_url}/iserver/auth/status",
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("authenticated"):
                return True, "Interactive Brokers authentication successful"
            else:
                return False, "Not authenticated - login via Gateway/TWS required"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"IB error: {str(e)}"

