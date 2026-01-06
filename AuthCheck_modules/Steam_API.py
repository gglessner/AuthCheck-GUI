"""Steam Web API authentication module."""

module_description = "Steam (Gaming)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "Steam Web API Key", "default": ""},
    {"name": "steam_id", "type": "text", "label": "Steam ID (for testing)", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Get API key from steamcommunity.com/dev/apikey. SteamID: 17-digit number."}
]

def authenticate(form_data):
    """Test Steam Web API authentication."""
    try:
        import requests
        
        api_key = form_data.get("api_key", "")
        steam_id = form_data.get("steam_id", "")
        
        # Test API key with GetPlayerSummaries if we have a steam_id, otherwise use GetAppList
        if steam_id:
            url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
            params = {"key": api_key, "steamids": steam_id}
        else:
            url = f"https://api.steampowered.com/ISteamApps/GetAppList/v2/"
            params = {"key": api_key}
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            return True, "Steam API authentication successful"
        elif response.status_code == 403:
            return False, "Invalid API key"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Steam API error: {str(e)}"

