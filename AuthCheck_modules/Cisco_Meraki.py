# Cisco Meraki Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Cisco Meraki (Network)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "org_id", "type": "text", "label": "Organization ID (Optional)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API key from Dashboard > Organization > Settings > API access."},
]


def authenticate(form_data):
    """Attempt to authenticate to Cisco Meraki."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    api_key = form_data.get('api_key', '').strip()
    org_id = form_data.get('org_id', '').strip()
    
    if not api_key:
        return False, "API Key is required"
    
    try:
        headers = {
            'X-Cisco-Meraki-API-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        # Get organizations
        response = requests.get("https://api.meraki.com/api/v1/organizations",
                               headers=headers, timeout=15)
        
        if response.status_code == 200:
            orgs = response.json()
            org_count = len(orgs)
            org_names = [o['name'] for o in orgs[:3]]
            
            if org_id:
                # Get specific org info
                org_resp = requests.get(f"https://api.meraki.com/api/v1/organizations/{org_id}",
                                       headers=headers, timeout=10)
                
                if org_resp.status_code == 200:
                    org = org_resp.json()
                    org_name = org.get('name', 'unknown')
                    
                    # Get network count
                    networks_resp = requests.get(
                        f"https://api.meraki.com/api/v1/organizations/{org_id}/networks",
                        headers=headers, timeout=10)
                    network_count = 0
                    if networks_resp.status_code == 200:
                        network_count = len(networks_resp.json())
                    
                    # Get device count
                    devices_resp = requests.get(
                        f"https://api.meraki.com/api/v1/organizations/{org_id}/devices",
                        headers=headers, timeout=10)
                    device_count = 0
                    if devices_resp.status_code == 200:
                        device_count = len(devices_resp.json())
                    
                    return True, f"Successfully authenticated to Cisco Meraki\nOrganization: {org_name}\nNetworks: {network_count}\nDevices: {device_count}"
            
            return True, f"Successfully authenticated to Cisco Meraki\nOrganizations: {org_count}\nSample: {', '.join(org_names)}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API key"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Meraki error: {e}"

