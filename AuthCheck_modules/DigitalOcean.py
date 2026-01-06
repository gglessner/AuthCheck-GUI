# DigitalOcean Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "DigitalOcean (Cloud)"

form_fields = [
    {"name": "api_token", "type": "password", "label": "API Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Personal access token from cloud.digitalocean.com/account/api/tokens."},
]


def authenticate(form_data):
    """Attempt to authenticate to DigitalOcean."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    api_token = form_data.get('api_token', '').strip()
    
    if not api_token:
        return False, "API Token is required"
    
    try:
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        # Get account info
        response = requests.get("https://api.digitalocean.com/v2/account",
                               headers=headers, timeout=15)
        
        if response.status_code == 200:
            account = response.json().get('account', {})
            email = account.get('email', 'unknown')
            status = account.get('status', 'unknown')
            droplet_limit = account.get('droplet_limit', 0)
            
            # Get droplet count
            droplets_resp = requests.get("https://api.digitalocean.com/v2/droplets",
                                        headers=headers, timeout=10)
            droplet_count = 0
            if droplets_resp.status_code == 200:
                droplet_count = droplets_resp.json().get('meta', {}).get('total', 0)
            
            # Get kubernetes cluster count
            k8s_resp = requests.get("https://api.digitalocean.com/v2/kubernetes/clusters",
                                   headers=headers, timeout=10)
            k8s_count = 0
            if k8s_resp.status_code == 200:
                k8s_count = len(k8s_resp.json().get('kubernetes_clusters', []))
            
            # Get database count
            db_resp = requests.get("https://api.digitalocean.com/v2/databases",
                                  headers=headers, timeout=10)
            db_count = 0
            if db_resp.status_code == 200:
                db_count = len(db_resp.json().get('databases', []))
            
            return True, f"Successfully authenticated to DigitalOcean\nEmail: {email}\nStatus: {status}\nDroplets: {droplet_count}/{droplet_limit}\nK8s Clusters: {k8s_count}\nDatabases: {db_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"DigitalOcean error: {e}"

