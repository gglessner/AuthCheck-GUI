"""Lightspeed POS authentication module."""

module_description = "Lightspeed (POS)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "refresh_token", "type": "password", "label": "Refresh Token", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["Retail (R-Series)", "Restaurant (L-Series)", "eCommerce (C-Series)"], "default": "Retail (R-Series)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Lightspeed POS. OAuth2 flow required. Get refresh token from OAuth flow."}
]

def authenticate(form_data):
    """Test Lightspeed authentication."""
    try:
        import requests
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        refresh_token = form_data.get("refresh_token", "")
        product = form_data.get("product", "Retail (R-Series)")
        
        # Determine API endpoint based on product
        if "Restaurant" in product:
            token_url = "https://cloud.lightspeedapp.com/oauth/access_token.php"
        else:
            token_url = "https://cloud.lightspeedapp.com/oauth/access_token.php"
        
        response = requests.post(
            token_url,
            data={
                "grant_type": "refresh_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token
            },
            timeout=30
        )
        
        if response.status_code == 200 and "access_token" in response.json():
            return True, "Lightspeed authentication successful"
        else:
            return False, f"Auth failed: {response.text}"
            
    except Exception as e:
        return False, f"Lightspeed error: {str(e)}"

