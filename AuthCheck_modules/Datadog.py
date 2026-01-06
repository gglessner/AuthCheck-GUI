# Datadog Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Datadog (Monitoring)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "app_key", "type": "password", "label": "Application Key"},
    {"name": "site", "type": "combo", "label": "Datadog Site", "options": ["datadoghq.com", "datadoghq.eu", "us3.datadoghq.com", "us5.datadoghq.com", "ddog-gov.com"], "default": "datadoghq.com"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API Key: 32-char hex. App Key: 40-char hex. Both from Organization Settings > API Keys."},
]


def authenticate(form_data):
    """Attempt to authenticate to Datadog."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    api_key = form_data.get('api_key', '').strip()
    app_key = form_data.get('app_key', '').strip()
    site = form_data.get('site', 'datadoghq.com')
    
    if not api_key:
        return False, "API Key is required"
    if not app_key:
        return False, "Application Key is required"
    
    try:
        base_url = f"https://api.{site}"
        
        headers = {
            'DD-API-KEY': api_key,
            'DD-APPLICATION-KEY': app_key,
            'Content-Type': 'application/json'
        }
        
        # Validate API key
        response = requests.get(f"{base_url}/api/v1/validate", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            valid = data.get('valid', False)
            
            if valid:
                # Get organization info
                org_resp = requests.get(f"{base_url}/api/v1/org", headers=headers, timeout=10)
                org_name = 'unknown'
                if org_resp.status_code == 200:
                    org_data = org_resp.json()
                    org_name = org_data.get('org', {}).get('name', 'unknown')
                
                # Get current user
                user_resp = requests.get(f"{base_url}/api/v2/current_user", headers=headers, timeout=10)
                user_email = 'unknown'
                if user_resp.status_code == 200:
                    user_data = user_resp.json()
                    user_email = user_data.get('data', {}).get('attributes', {}).get('email', 'unknown')
                
                return True, f"Successfully authenticated to Datadog\nSite: {site}\nOrganization: {org_name}\nUser: {user_email}"
            else:
                return False, "API key validation failed"
        elif response.status_code == 403:
            return False, "Authentication failed: Invalid API or Application key"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Datadog error: {e}"

