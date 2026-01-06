"""Discord API authentication module."""

module_description = "Discord (Collaboration)"

form_fields = [
    {"name": "bot_token", "type": "password", "label": "Bot Token", "default": ""},
    {"name": "client_id", "type": "text", "label": "Application Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["Bot Token", "Client Credentials"], "default": "Bot Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Bot token from Developer Portal > Bot. Never share bot tokens!"}
]

def authenticate(form_data):
    """Test Discord API authentication."""
    try:
        import requests
        
        auth_type = form_data.get("auth_type", "Bot Token")
        bot_token = form_data.get("bot_token", "")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        
        if auth_type == "Bot Token":
            response = requests.get(
                "https://discord.com/api/v10/users/@me",
                headers={"Authorization": f"Bot {bot_token}"},
                timeout=30
            )
            
            if response.status_code == 200:
                user = response.json()
                return True, f"Discord Bot authentication successful (Bot: {user.get('username')})"
            else:
                return False, f"Bot auth failed: {response.text}"
        else:
            # Client credentials flow
            token_response = requests.post(
                "https://discord.com/api/v10/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "scope": "identify"
                },
                auth=(client_id, client_secret),
                timeout=30
            )
            
            if token_response.status_code == 200:
                return True, "Discord OAuth2 authentication successful"
            else:
                return False, f"OAuth2 failed: {token_response.text}"
            
    except Exception as e:
        return False, f"Discord error: {str(e)}"

