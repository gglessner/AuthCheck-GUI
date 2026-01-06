"""Schoology LMS authentication module."""

module_description = "Schoology (LMS)"

form_fields = [
    {"name": "consumer_key", "type": "text", "label": "Consumer Key", "default": ""},
    {"name": "consumer_secret", "type": "password", "label": "Consumer Secret", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Schoology (PowerSchool). OAuth1. Keys from System Settings > API."}
]

def authenticate(form_data):
    """Test Schoology authentication."""
    try:
        import requests
        from requests_oauthlib import OAuth1
        
        consumer_key = form_data.get("consumer_key", "")
        consumer_secret = form_data.get("consumer_secret", "")
        
        auth = OAuth1(consumer_key, consumer_secret, signature_type='auth_header')
        
        response = requests.get(
            "https://api.schoology.com/v1/users/me",
            auth=auth,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Schoology authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except ImportError:
        return False, "requests-oauthlib not installed. Install with: pip install requests-oauthlib"
    except Exception as e:
        return False, f"Schoology error: {str(e)}"

