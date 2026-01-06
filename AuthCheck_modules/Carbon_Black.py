# VMware Carbon Black Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "VMware Carbon Black (EDR)"

form_fields = [
    {"name": "url", "type": "text", "label": "CBC URL"},
    {"name": "org_key", "type": "text", "label": "Organization Key"},
    {"name": "api_id", "type": "text", "label": "API ID"},
    {"name": "api_secret", "type": "password", "label": "API Secret Key"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API credentials from Settings > API Access. Org Key from Settings > Organization."},
]


def authenticate(form_data):
    """Attempt to authenticate to VMware Carbon Black Cloud."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', '').strip()
    org_key = form_data.get('org_key', '').strip()
    api_id = form_data.get('api_id', '').strip()
    api_secret = form_data.get('api_secret', '')
    
    if not url:
        return False, "CBC URL is required"
    if not org_key:
        return False, "Organization Key is required"
    if not api_id or not api_secret:
        return False, "API ID and Secret are required"
    
    if not url.startswith('http'):
        url = f"https://{url}"
    url = url.rstrip('/')
    
    try:
        headers = {
            'X-Auth-Token': f'{api_secret}/{api_id}',
            'Content-Type': 'application/json'
        }
        
        # Get organization info
        response = requests.get(f"{url}/appservices/v6/orgs/{org_key}/alerts/_search",
                               headers=headers, 
                               json={"rows": 1, "criteria": {"workflow": ["OPEN"]}},
                               timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            alert_count = data.get('num_found', 0)
            
            # Get device count
            devices_resp = requests.post(
                f"{url}/appservices/v6/orgs/{org_key}/devices/_search",
                headers=headers,
                json={"rows": 1},
                timeout=10)
            device_count = 0
            if devices_resp.status_code == 200:
                device_count = devices_resp.json().get('num_found', 0)
            
            return True, f"Successfully authenticated to Carbon Black Cloud\nOrg Key: {org_key}\nDevices: {device_count}\nOpen Alerts: {alert_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Authentication failed: Access denied"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Carbon Black error: {e}"

