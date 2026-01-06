# LibreNMS Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "LibreNMS (Monitoring)"

form_fields = [
    {"name": "url", "type": "text", "label": "LibreNMS URL"},
    {"name": "api_token", "type": "password", "label": "API Token"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API token from Settings > API > API Settings. Default port 80/443."},
]


def authenticate(form_data):
    """Attempt to authenticate to LibreNMS."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', '').strip()
    api_token = form_data.get('api_token', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not url:
        return False, "LibreNMS URL is required"
    if not api_token:
        return False, "API Token is required"
    
    if not url.startswith('http'):
        url = f"https://{url}"
    url = url.rstrip('/')
    
    try:
        headers = {
            'X-Auth-Token': api_token,
            'Accept': 'application/json'
        }
        
        # Get system info
        response = requests.get(
            f"{url}/api/v0/system",
            headers=headers,
            verify=verify_ssl,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('system', [{}])[0].get('local_ver', 'unknown') if data.get('system') else 'unknown'
            
            # Get device count
            devices_resp = requests.get(
                f"{url}/api/v0/devices",
                headers=headers,
                verify=verify_ssl,
                timeout=10
            )
            device_count = 0
            if devices_resp.status_code == 200:
                device_count = devices_resp.json().get('count', 0)
            
            # Get alerts count
            alerts_resp = requests.get(
                f"{url}/api/v0/alerts?state=1",
                headers=headers,
                verify=verify_ssl,
                timeout=10
            )
            alert_count = 0
            if alerts_resp.status_code == 200:
                alert_count = len(alerts_resp.json().get('alerts', []))
            
            return True, f"Successfully authenticated to LibreNMS\nVersion: {version}\nDevices: {device_count}\nActive Alerts: {alert_count}"
        elif response.status_code == 401 or response.status_code == 403:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"LibreNMS error: {e}"

