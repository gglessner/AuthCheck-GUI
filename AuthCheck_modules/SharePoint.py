"""SharePoint authentication module."""

module_description = "SharePoint (Document)"

form_fields = [
    {"name": "site_url", "type": "text", "label": "Site URL", "default": ""},
    {"name": "tenant_id", "type": "text", "label": "Tenant ID", "default": ""},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "username", "type": "text", "label": "Username (Legacy)", "default": ""},
    {"name": "password", "type": "password", "label": "Password (Legacy)", "default": ""},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["App-Only", "User Credentials"], "default": "App-Only"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "SharePoint Online. App registration in Azure AD. On-prem uses NTLM."}
]

def authenticate(form_data):
    """Test SharePoint authentication."""
    try:
        import requests
        
        site_url = form_data.get("site_url", "").rstrip("/")
        tenant_id = form_data.get("tenant_id", "")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        auth_type = form_data.get("auth_type", "App-Only")
        
        # Extract tenant from site URL for SharePoint Online
        if "sharepoint.com" in site_url:
            # Get access token
            resource = f"{site_url.split('.sharepoint.com')[0]}.sharepoint.com"
            
            token_response = requests.post(
                f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "scope": f"{resource}/.default"
                },
                timeout=30
            )
            
            if token_response.status_code != 200:
                return False, f"Token error: {token_response.text}"
            
            access_token = token_response.json().get("access_token")
            
            response = requests.get(
                f"{site_url}/_api/web/title",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                },
                timeout=30
            )
        else:
            # On-premises - try NTLM
            from requests_ntlm import HttpNtlmAuth
            username = form_data.get("username", "")
            password = form_data.get("password", "")
            
            response = requests.get(
                f"{site_url}/_api/web/title",
                auth=HttpNtlmAuth(username, password),
                headers={"Accept": "application/json"},
                timeout=30
            )
        
        if response.status_code == 200:
            return True, "SharePoint authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except ImportError:
        return False, "requests-ntlm library not installed for on-prem. Install with: pip install requests-ntlm"
    except Exception as e:
        return False, f"SharePoint error: {str(e)}"
