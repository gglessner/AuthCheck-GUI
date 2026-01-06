# HubSpot Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "HubSpot (CRM)"

form_fields = [
    {"name": "access_token", "type": "password", "label": "Private App Access Token"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Private app token from Settings > Integrations > Private Apps. Starts with pat-..."},
]


def authenticate(form_data):
    """Attempt to authenticate to HubSpot."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    access_token = form_data.get('access_token', '').strip()
    
    if not access_token:
        return False, "Private App Access Token is required"
    
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Get account info
        response = requests.get(
            "https://api.hubapi.com/account-info/v3/details",
            headers=headers, timeout=15
        )
        
        if response.status_code == 200:
            account = response.json()
            portal_id = account.get('portalId', 'unknown')
            time_zone = account.get('timeZone', 'unknown')
            
            # Get contact count
            contacts_resp = requests.get(
                "https://api.hubapi.com/crm/v3/objects/contacts?limit=1",
                headers=headers, timeout=10
            )
            contact_count = 0
            if contacts_resp.status_code == 200:
                contact_count = contacts_resp.json().get('total', 0)
            
            # Get company count
            companies_resp = requests.get(
                "https://api.hubapi.com/crm/v3/objects/companies?limit=1",
                headers=headers, timeout=10
            )
            company_count = 0
            if companies_resp.status_code == 200:
                company_count = companies_resp.json().get('total', 0)
            
            # Get deal count
            deals_resp = requests.get(
                "https://api.hubapi.com/crm/v3/objects/deals?limit=1",
                headers=headers, timeout=10
            )
            deal_count = 0
            if deals_resp.status_code == 200:
                deal_count = deals_resp.json().get('total', 0)
            
            return True, f"Successfully authenticated to HubSpot\nPortal ID: {portal_id}\nTimezone: {time_zone}\nContacts: {contact_count}\nCompanies: {company_count}\nDeals: {deal_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"HubSpot error: {e}"

