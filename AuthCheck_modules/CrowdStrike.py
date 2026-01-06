# CrowdStrike Falcon Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "CrowdStrike Falcon (EDR)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "API Client ID"},
    {"name": "client_secret", "type": "password", "label": "API Client Secret"},
    {"name": "base_url", "type": "combo", "label": "Cloud", "options": ["https://api.crowdstrike.com", "https://api.us-2.crowdstrike.com", "https://api.eu-1.crowdstrike.com", "https://api.laggar.gcw.crowdstrike.com"], "default": "https://api.crowdstrike.com"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API credentials from Falcon Console > Support > API Clients and Keys."},
]


def authenticate(form_data):
    """Attempt to authenticate to CrowdStrike Falcon."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '')
    base_url = form_data.get('base_url', 'https://api.crowdstrike.com')
    
    if not client_id:
        return False, "API Client ID is required"
    if not client_secret:
        return False, "API Client Secret is required"
    
    try:
        # Get OAuth2 token
        token_resp = requests.post(
            f"{base_url}/oauth2/token",
            data={'client_id': client_id, 'client_secret': client_secret},
            timeout=15
        )
        
        if token_resp.status_code == 201:
            access_token = token_resp.json().get('access_token')
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Get sensor info
            sensors_resp = requests.get(
                f"{base_url}/sensors/queries/sensors/v1?limit=1",
                headers=headers, timeout=10)
            sensor_count = 0
            if sensors_resp.status_code == 200:
                sensor_count = sensors_resp.json().get('meta', {}).get('pagination', {}).get('total', 0)
            
            # Get detection count
            detections_resp = requests.get(
                f"{base_url}/detects/queries/detects/v1?filter=status:'new'&limit=1",
                headers=headers, timeout=10)
            detection_count = 0
            if detections_resp.status_code == 200:
                detection_count = detections_resp.json().get('meta', {}).get('pagination', {}).get('total', 0)
            
            # Get host count
            hosts_resp = requests.get(
                f"{base_url}/devices/queries/devices/v1?limit=1",
                headers=headers, timeout=10)
            host_count = 0
            if hosts_resp.status_code == 200:
                host_count = hosts_resp.json().get('meta', {}).get('pagination', {}).get('total', 0)
            
            return True, f"Successfully authenticated to CrowdStrike Falcon\nHosts: {host_count}\nSensors: {sensor_count}\nNew Detections: {detection_count}"
        elif token_resp.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif token_resp.status_code == 403:
            return False, "Authentication failed: Access denied"
        else:
            return False, f"HTTP {token_resp.status_code}: {token_resp.text[:200]}"
            
    except Exception as e:
        return False, f"CrowdStrike error: {e}"

