# Sumo Logic Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Sumo Logic (Monitoring)"

form_fields = [
    {"name": "access_id", "type": "text", "label": "Access ID"},
    {"name": "access_key", "type": "password", "label": "Access Key"},
    {"name": "deployment", "type": "combo", "label": "Deployment", "options": ["us1", "us2", "eu", "au", "de", "jp", "ca", "in", "fed"], "default": "us2"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Access ID/Key from Administration > Security > Access Keys. Deployment from URL."},
]


def authenticate(form_data):
    """Attempt to authenticate to Sumo Logic."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    access_id = form_data.get('access_id', '').strip()
    access_key = form_data.get('access_key', '')
    deployment = form_data.get('deployment', 'us2')
    
    if not access_id:
        return False, "Access ID is required"
    if not access_key:
        return False, "Access Key is required"
    
    try:
        # Regional API endpoints
        endpoints = {
            'us1': 'https://api.sumologic.com/api',
            'us2': 'https://api.us2.sumologic.com/api',
            'eu': 'https://api.eu.sumologic.com/api',
            'au': 'https://api.au.sumologic.com/api',
            'de': 'https://api.de.sumologic.com/api',
            'jp': 'https://api.jp.sumologic.com/api',
            'ca': 'https://api.ca.sumologic.com/api',
            'in': 'https://api.in.sumologic.com/api',
            'fed': 'https://api.fed.sumologic.com/api'
        }
        
        base_url = endpoints.get(deployment, endpoints['us2'])
        auth = HTTPBasicAuth(access_id, access_key)
        
        # Get account info
        response = requests.get(f"{base_url}/v1/account/contract",
                               auth=auth, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            org_id = data.get('orgId', 'unknown')
            plan_type = data.get('planType', 'unknown')
            
            # Get collector count
            collectors_resp = requests.get(f"{base_url}/v1/collectors",
                                          auth=auth, timeout=10)
            collector_count = 0
            if collectors_resp.status_code == 200:
                collector_count = len(collectors_resp.json().get('collectors', []))
            
            return True, f"Successfully authenticated to Sumo Logic\nDeployment: {deployment}\nOrg ID: {org_id}\nPlan: {plan_type}\nCollectors: {collector_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Sumo Logic error: {e}"

