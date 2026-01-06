# Tenable.io / Nessus Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Tenable.io / Nessus (Security)"

form_fields = [
    {"name": "platform", "type": "combo", "label": "Platform", "options": ["Tenable.io", "Nessus"], "default": "Tenable.io"},
    {"name": "url", "type": "text", "label": "URL (Nessus only)", "default": "https://localhost:8834"},
    {"name": "access_key", "type": "text", "label": "Access Key"},
    {"name": "secret_key", "type": "password", "label": "Secret Key"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API keys from Settings > My Account > API Keys. Nessus default port 8834."},
]


def authenticate(form_data):
    """Attempt to authenticate to Tenable.io or Nessus."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    platform = form_data.get('platform', 'Tenable.io')
    url = form_data.get('url', 'https://localhost:8834').strip()
    access_key = form_data.get('access_key', '').strip()
    secret_key = form_data.get('secret_key', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not access_key:
        return False, "Access Key is required"
    if not secret_key:
        return False, "Secret Key is required"
    
    try:
        if platform == "Tenable.io":
            base_url = "https://cloud.tenable.com"
        else:
            base_url = url.rstrip('/')
        
        headers = {
            'X-ApiKeys': f'accessKey={access_key}; secretKey={secret_key}',
            'Accept': 'application/json'
        }
        
        session = requests.Session()
        session.verify = verify_ssl
        
        # Get server info
        if platform == "Tenable.io":
            response = session.get(f"{base_url}/server/status",
                                  headers=headers, timeout=15)
        else:
            response = session.get(f"{base_url}/server/properties",
                                  headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if platform == "Tenable.io":
                # Get asset count
                assets_resp = session.get(f"{base_url}/assets",
                                         headers=headers, timeout=10)
                asset_count = 0
                if assets_resp.status_code == 200:
                    asset_count = len(assets_resp.json().get('assets', []))
                
                # Get scan count
                scans_resp = session.get(f"{base_url}/scans",
                                        headers=headers, timeout=10)
                scan_count = 0
                if scans_resp.status_code == 200:
                    scan_count = len(scans_resp.json().get('scans', []))
                
                return True, f"Successfully authenticated to Tenable.io\nAssets: {asset_count}\nScans: {scan_count}"
            else:
                version = data.get('server_version', 'unknown')
                
                # Get scan count
                scans_resp = session.get(f"{base_url}/scans",
                                        headers=headers, timeout=10)
                scan_count = 0
                if scans_resp.status_code == 200:
                    scan_count = len(scans_resp.json().get('scans', []))
                
                return True, f"Successfully authenticated to Nessus {version}\nScans: {scan_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid API keys"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Tenable error: {e}"

