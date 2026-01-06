# Linode (Akamai Cloud) Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Linode / Akamai Cloud (Cloud)"

form_fields = [
    {"name": "api_token", "type": "password", "label": "Personal Access Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "PAT from cloud.linode.com/profile/tokens."},
]


def authenticate(form_data):
    """Attempt to authenticate to Linode."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    api_token = form_data.get('api_token', '').strip()
    
    if not api_token:
        return False, "Personal Access Token is required"
    
    try:
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        # Get account info
        response = requests.get("https://api.linode.com/v4/account",
                               headers=headers, timeout=15)
        
        if response.status_code == 200:
            account = response.json()
            email = account.get('email', 'unknown')
            company = account.get('company', 'N/A')
            balance = account.get('balance', 0)
            
            # Get Linode count
            linodes_resp = requests.get("https://api.linode.com/v4/linode/instances",
                                       headers=headers, timeout=10)
            linode_count = 0
            if linodes_resp.status_code == 200:
                linode_count = linodes_resp.json().get('results', 0)
            
            # Get volume count
            volumes_resp = requests.get("https://api.linode.com/v4/volumes",
                                       headers=headers, timeout=10)
            volume_count = 0
            if volumes_resp.status_code == 200:
                volume_count = volumes_resp.json().get('results', 0)
            
            # Get domain count
            domains_resp = requests.get("https://api.linode.com/v4/domains",
                                       headers=headers, timeout=10)
            domain_count = 0
            if domains_resp.status_code == 200:
                domain_count = domains_resp.json().get('results', 0)
            
            return True, f"Successfully authenticated to Linode\nEmail: {email}\nCompany: {company}\nBalance: ${balance:.2f}\nLinodes: {linode_count}\nVolumes: {volume_count}\nDomains: {domain_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Linode error: {e}"

