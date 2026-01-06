"""NetSuite authentication module."""

module_description = "NetSuite (ERP)"

form_fields = [
    {"name": "account_id", "type": "text", "label": "Account ID", "default": ""},
    {"name": "consumer_key", "type": "text", "label": "Consumer Key", "default": ""},
    {"name": "consumer_secret", "type": "password", "label": "Consumer Secret", "default": ""},
    {"name": "token_id", "type": "text", "label": "Token ID", "default": ""},
    {"name": "token_secret", "type": "password", "label": "Token Secret", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "NetSuite TBA (Token-Based Auth). Setup > Integration > Manage Tokens."}
]

def authenticate(form_data):
    """Test NetSuite authentication."""
    try:
        import requests
        from requests_oauthlib import OAuth1
        
        account_id = form_data.get("account_id", "")
        consumer_key = form_data.get("consumer_key", "")
        consumer_secret = form_data.get("consumer_secret", "")
        token_id = form_data.get("token_id", "")
        token_secret = form_data.get("token_secret", "")
        
        # NetSuite realm format
        realm = account_id.replace("-", "_").upper()
        
        base_url = f"https://{account_id}.suitetalk.api.netsuite.com/services/rest/record/v1"
        
        auth = OAuth1(
            consumer_key,
            consumer_secret,
            token_id,
            token_secret,
            realm=realm,
            signature_method='HMAC-SHA256'
        )
        
        response = requests.get(
            f"{base_url}/customer",
            auth=auth,
            params={"limit": 1},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "NetSuite authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except ImportError:
        return False, "requests-oauthlib library not installed. Install with: pip install requests-oauthlib"
    except Exception as e:
        return False, f"NetSuite error: {str(e)}"

