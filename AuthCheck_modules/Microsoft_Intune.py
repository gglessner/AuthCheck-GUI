"""Microsoft Intune authentication module."""

module_description = "Microsoft Intune (MDM)"

form_fields = [
    {"name": "tenant_id", "type": "text", "label": "Tenant ID", "default": ""},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Azure AD app registration. Requires DeviceManagementManagedDevices.Read.All permission."}
]

def authenticate(form_data):
    """Test Microsoft Intune authentication."""
    try:
        import requests
        
        tenant_id = form_data.get("tenant_id", "")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        
        # Get access token
        token_response = requests.post(
            f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "https://graph.microsoft.com/.default"
            },
            timeout=30
        )
        
        if token_response.status_code != 200:
            return False, f"Token request failed: {token_response.text}"
        
        access_token = token_response.json().get("access_token")
        
        # Test Intune API
        response = requests.get(
            "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"$top": 1},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Microsoft Intune authentication successful"
        else:
            return False, f"Intune API error: HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Intune error: {str(e)}"

