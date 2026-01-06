# Palo Alto Networks Firewall Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Palo Alto Networks Firewall (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "Firewall Host"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "api_key", "type": "password", "label": "API Key (Alternative)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / admin (default, must change on first login). API key from Device > Setup > Management."},
]


def authenticate(form_data):
    """Attempt to authenticate to Palo Alto Networks Firewall."""
    try:
        import requests
        import xml.etree.ElementTree as ET
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    api_key = form_data.get('api_key', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Firewall Host is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        if api_key:
            key = api_key
        else:
            if not username:
                return False, "Username or API Key is required"
            
            # Get API key
            keygen_url = f"{host}/api/?type=keygen&user={username}&password={password}"
            keygen_resp = session.get(keygen_url, timeout=10)
            
            if keygen_resp.status_code != 200:
                return False, f"Failed to get API key: HTTP {keygen_resp.status_code}"
            
            root = ET.fromstring(keygen_resp.text)
            status = root.get('status')
            
            if status != 'success':
                msg = root.find('.//msg')
                error_msg = msg.text if msg is not None else 'Unknown error'
                return False, f"Authentication failed: {error_msg}"
            
            key_elem = root.find('.//key')
            if key_elem is None:
                return False, "Failed to retrieve API key"
            key = key_elem.text
        
        # Get system info
        sysinfo_url = f"{host}/api/?type=op&cmd=<show><system><info></info></system></show>&key={key}"
        response = session.get(sysinfo_url, timeout=10)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            status = root.get('status')
            
            if status == 'success':
                result = root.find('.//result/system')
                if result is not None:
                    hostname = result.findtext('hostname', 'unknown')
                    model = result.findtext('model', 'unknown')
                    sw_version = result.findtext('sw-version', 'unknown')
                    serial = result.findtext('serial', 'unknown')
                    
                    return True, f"Successfully authenticated to Palo Alto Firewall\nHostname: {hostname}\nModel: {model}\nPAN-OS: {sw_version}\nSerial: {serial}"
                else:
                    return True, f"Successfully authenticated to Palo Alto Firewall at {host}"
            else:
                msg = root.find('.//msg/line')
                error_msg = msg.text if msg is not None else 'Unknown error'
                return False, f"API error: {error_msg}"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except ET.ParseError as e:
        return False, f"XML parse error: {e}"
    except Exception as e:
        return False, f"Palo Alto error: {e}"

