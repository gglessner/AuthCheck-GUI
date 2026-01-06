"""Wave accounting authentication module."""

module_description = "Wave (Accounting)"

form_fields = [
    {"name": "access_token", "type": "password", "label": "Full Access Token", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Wave Accounting. GraphQL API. Get token from Wave Connect."}
]

def authenticate(form_data):
    """Test Wave authentication."""
    try:
        import requests
        
        access_token = form_data.get("access_token", "")
        
        query = """
        query {
            user {
                id
                firstName
                lastName
            }
        }
        """
        
        response = requests.post(
            "https://gql.waveapps.com/graphql/public",
            json={"query": query},
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("data", {}).get("user"):
                user = data["data"]["user"]
                name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
                return True, f"Wave authentication successful ({name})"
            else:
                return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Wave error: {str(e)}"

