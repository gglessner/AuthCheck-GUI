"""PlayStation Network API authentication module."""

module_description = "PlayStation Network (Gaming)"

form_fields = [
    {"name": "npsso", "type": "password", "label": "NPSSO Token", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Get NPSSO from store.playstation.com cookies after login. Expires in 60 days."}
]

def authenticate(form_data):
    """Test PlayStation Network authentication."""
    try:
        from psnawp_api import PSNAWP
        
        npsso = form_data.get("npsso", "")
        
        psnawp = PSNAWP(npsso)
        
        # Get authenticated user info
        client = psnawp.me()
        online_id = client.online_id
        
        return True, f"PSN authentication successful (User: {online_id})"
        
    except ImportError:
        return False, "psnawp-api library not installed. Install with: pip install psnawp-api"
    except Exception as e:
        return False, f"PSN error: {str(e)}"

