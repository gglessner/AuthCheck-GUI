# Informatica Cloud Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Informatica Cloud (BigData)"

form_fields = [
    {"name": "region", "type": "combo", "label": "Region", "options": ["us", "em", "ap"], "default": "us"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Username is email. Regions: us (US), em (EMEA), ap (APAC). From administrator.informatica.com."},
]


def authenticate(form_data):
    """Attempt to authenticate to Informatica Cloud (IICS)."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    region = form_data.get('region', 'us')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    if not username:
        return False, "Username is required"
    if not password:
        return False, "Password is required"
    
    try:
        # Regional login URLs
        login_urls = {
            'us': 'https://dm-us.informaticacloud.com/saas/public/core/v3/login',
            'em': 'https://dm-em.informaticacloud.com/saas/public/core/v3/login',
            'ap': 'https://dm-ap.informaticacloud.com/saas/public/core/v3/login'
        }
        
        login_url = login_urls.get(region, login_urls['us'])
        
        headers = {'Content-Type': 'application/json'}
        login_data = {
            'username': username,
            'password': password
        }
        
        response = requests.post(login_url, json=login_data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            session_id = data.get('sessionId')
            user_info = data.get('userInfo', {})
            org_info = data.get('orgInfo', {})
            
            user_name = user_info.get('name', username)
            org_name = org_info.get('name', 'unknown')
            org_id = org_info.get('id', 'unknown')
            
            # Get products
            products = data.get('products', [])
            product_names = [p.get('name', 'unknown') for p in products[:5]]
            
            return True, f"Successfully authenticated to Informatica Cloud\nOrganization: {org_name}\nUser: {user_name}\nRegion: {region.upper()}\nProducts: {', '.join(product_names)}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', response.text[:200])
            except:
                error_msg = response.text[:200]
            return False, f"Authentication failed: {error_msg}"
            
    except Exception as e:
        return False, f"Informatica error: {e}"

