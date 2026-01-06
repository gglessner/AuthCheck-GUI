# Rapid7 InsightVM Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Rapid7 InsightVM (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "Console Host"},
    {"name": "port", "type": "text", "label": "API Port", "default": "3780"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "(set at install). Default port 3780. API v3 endpoints at /api/3/"},
]


def authenticate(form_data):
    """Attempt to authenticate to Rapid7 InsightVM."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '3780').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Console Host is required"
    if not username:
        return False, "Username is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        auth = HTTPBasicAuth(username, password)
        session = requests.Session()
        session.verify = verify_ssl
        
        # Get admin info
        response = session.get(f"{host}:{port}/api/3/administration/info",
                              auth=auth, timeout=15)
        
        if response.status_code == 200:
            info = response.json()
            version = info.get('version', 'unknown')
            
            # Get asset count
            assets_resp = session.get(f"{host}:{port}/api/3/assets?size=1",
                                     auth=auth, timeout=10)
            asset_count = 0
            if assets_resp.status_code == 200:
                asset_count = assets_resp.json().get('page', {}).get('totalResources', 0)
            
            # Get site count
            sites_resp = session.get(f"{host}:{port}/api/3/sites",
                                    auth=auth, timeout=10)
            site_count = 0
            if sites_resp.status_code == 200:
                site_count = len(sites_resp.json().get('resources', []))
            
            # Get scan engine count
            engines_resp = session.get(f"{host}:{port}/api/3/scan_engines",
                                      auth=auth, timeout=10)
            engine_count = 0
            if engines_resp.status_code == 200:
                engine_count = len(engines_resp.json().get('resources', []))
            
            return True, f"Successfully authenticated to InsightVM {version}\nAssets: {asset_count}\nSites: {site_count}\nScan Engines: {engine_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"InsightVM error: {e}"

