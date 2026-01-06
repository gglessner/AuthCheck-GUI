"""Jellyfin Media Server authentication module."""

module_description = "Jellyfin (Media)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8096",
     "port_toggle": "use_ssl", "tls_port": "8920", "non_tls_port": "8096"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "api_key", "type": "password", "label": "API Key (alternative)", "default": ""},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8920, Non-TLS: 8096. API key from Dashboard. First run: no password."}
]

def authenticate(form_data):
    """Test Jellyfin authentication."""
    try:
        import requests
        
        host = form_data.get("host", "localhost")
        port = form_data.get("port", "8096")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        api_key = form_data.get("api_key", "")
        use_ssl = form_data.get("use_ssl", False)
        
        protocol = "https" if use_ssl else "http"
        base_url = f"{protocol}://{host}:{port}"
        
        if api_key:
            response = requests.get(
                f"{base_url}/System/Info",
                headers={"X-Emby-Token": api_key},
                timeout=30
            )
        else:
            # Authenticate user
            auth_response = requests.post(
                f"{base_url}/Users/AuthenticateByName",
                json={"Username": username, "Pw": password},
                headers={
                    "X-Emby-Authorization": 'MediaBrowser Client="AuthCheck", Device="Python", DeviceId="authcheck", Version="1.0"',
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            if auth_response.status_code != 200:
                return False, f"Authentication failed: HTTP {auth_response.status_code}"
            
            token = auth_response.json().get("AccessToken")
            response = requests.get(
                f"{base_url}/System/Info",
                headers={"X-Emby-Token": token},
                timeout=30
            )
        
        if response.status_code == 200:
            info = response.json()
            return True, f"Jellyfin authentication successful (v{info.get('Version')})"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Jellyfin error: {str(e)}"

