# Terraform Cloud / Enterprise Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Terraform Cloud / Enterprise (CI/CD)"

form_fields = [
    {"name": "url", "type": "text", "label": "API URL", "default": "https://app.terraform.io"},
    {"name": "token", "type": "password", "label": "API Token"},
    {"name": "organization", "type": "text", "label": "Organization"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Token from User Settings > Tokens. For Enterprise, use your TFE URL."},
]


def authenticate(form_data):
    """Attempt to authenticate to Terraform Cloud/Enterprise."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', 'https://app.terraform.io').strip()
    token = form_data.get('token', '').strip()
    organization = form_data.get('organization', '').strip()
    
    if not token:
        return False, "API Token is required"
    
    url = url.rstrip('/')
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/vnd.api+json'
        }
        
        # Get account info
        response = requests.get(f"{url}/api/v2/account/details",
                               headers=headers, timeout=15)
        
        if response.status_code == 200:
            account = response.json().get('data', {}).get('attributes', {})
            username = account.get('username', 'unknown')
            email = account.get('email', 'unknown')
            
            if organization:
                # Get organization details
                org_resp = requests.get(f"{url}/api/v2/organizations/{organization}",
                                       headers=headers, timeout=10)
                
                if org_resp.status_code == 200:
                    org_data = org_resp.json().get('data', {}).get('attributes', {})
                    
                    # Get workspace count
                    ws_resp = requests.get(f"{url}/api/v2/organizations/{organization}/workspaces",
                                          headers=headers, timeout=10)
                    ws_count = 0
                    if ws_resp.status_code == 200:
                        ws_count = len(ws_resp.json().get('data', []))
                    
                    return True, f"Successfully authenticated to Terraform Cloud\nUser: {username}\nOrganization: {organization}\nWorkspaces: {ws_count}"
                else:
                    return True, f"Successfully authenticated to Terraform Cloud\nUser: {username} ({email})\nNote: Organization '{organization}' not accessible"
            
            # Get organizations
            orgs_resp = requests.get(f"{url}/api/v2/organizations",
                                    headers=headers, timeout=10)
            org_count = 0
            org_names = []
            if orgs_resp.status_code == 200:
                orgs = orgs_resp.json().get('data', [])
                org_count = len(orgs)
                org_names = [o['attributes']['name'] for o in orgs[:3]]
            
            return True, f"Successfully authenticated to Terraform Cloud\nUser: {username} ({email})\nOrganizations: {org_count}\nSample: {', '.join(org_names) if org_names else 'none'}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Terraform Cloud error: {e}"

