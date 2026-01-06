# Cisco Unified Communications Manager (CUCM) Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Cisco CUCM (PBX)"

form_fields = [
    {"name": "host", "type": "text", "label": "CUCM Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "8443"},
    {"name": "username", "type": "text", "label": "Username", "default": "administrator"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: administrator/(configured). AXL API port 8443."},
]


def authenticate(form_data):
    """Attempt to authenticate to Cisco CUCM."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8443').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "CUCM Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        base_url = f"https://{host}:{port}"
        
        # Try AXL API (Administrative XML)
        axl_url = f"{base_url}/axl/"
        
        # SOAP request to get version
        soap_body = """<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
                          xmlns:ns="http://www.cisco.com/AXL/API/14.0">
            <soapenv:Header/>
            <soapenv:Body>
                <ns:getCCMVersion sequence="1"/>
            </soapenv:Body>
        </soapenv:Envelope>"""
        
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'CUCM:DB ver=14.0 getCCMVersion'
        }
        
        response = requests.post(
            axl_url,
            data=soap_body,
            headers=headers,
            auth=(username, password),
            verify=verify_ssl,
            timeout=15
        )
        
        if response.status_code == 200:
            # Parse version from response
            import re
            version_match = re.search(r'<version>([^<]+)</version>', response.text)
            version = version_match.group(1) if version_match else 'unknown'
            
            return True, f"Successfully authenticated to Cisco CUCM\nHost: {host}:{port}\nVersion: {version}\nAXL API: Accessible"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 599:
            # Try serviceability API instead
            svc_url = f"{base_url}/perfmonservice2/services/PerfmonService"
            svc_resp = requests.get(svc_url, auth=(username, password), verify=verify_ssl, timeout=10)
            if svc_resp.status_code == 200:
                return True, f"Successfully authenticated to Cisco CUCM\nHost: {host}:{port}\nPerfmon API: Accessible"
            return False, f"HTTP {response.status_code}: AXL API may not be enabled"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Cisco CUCM error: {e}"

