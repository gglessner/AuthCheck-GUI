# Grandstream Device Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Grandstream (PBX)"

form_fields = [
    {"name": "host", "type": "text", "label": "Grandstream Host"},
    {"name": "port", "type": "text", "label": "HTTP Port", "default": "80"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password", "default": "admin"},
    {"name": "device_type", "type": "combo", "label": "Device Type", "options": ["UCM PBX", "IP Phone"], "default": "UCM PBX"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "UCM default: admin/admin. Phone default: admin/admin."},
]


def authenticate(form_data):
    """Attempt to authenticate to Grandstream device."""
    try:
        import requests
        import hashlib
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '80').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    device_type = form_data.get('device_type', 'UCM PBX')
    
    if not host:
        return False, "Grandstream Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        base_url = f"http://{host}:{port}"
        session = requests.Session()
        
        if device_type == 'UCM PBX':
            # UCM uses challenge-response
            # Get challenge
            challenge_resp = session.post(
                f"{base_url}/cgi",
                json={'action': 'challenge', 'user': username},
                timeout=15
            )
            
            if challenge_resp.status_code == 200:
                challenge_data = challenge_resp.json()
                challenge = challenge_data.get('challenge', '')
                
                if challenge:
                    # Calculate response
                    md5_pass = hashlib.md5(password.encode()).hexdigest()
                    token = hashlib.md5(f"{challenge}{md5_pass}".encode()).hexdigest()
                    
                    # Login
                    login_resp = session.post(
                        f"{base_url}/cgi",
                        json={'action': 'login', 'user': username, 'token': token},
                        timeout=15
                    )
                    
                    if login_resp.status_code == 200:
                        login_data = login_resp.json()
                        if login_data.get('status') == 0:
                            cookie = login_data.get('cookie', '')
                            
                            # Get system info
                            info_resp = session.post(
                                f"{base_url}/cgi",
                                json={'action': 'getSystemInfo', 'cookie': cookie},
                                timeout=10
                            )
                            
                            model = 'UCM'
                            firmware = 'unknown'
                            if info_resp.status_code == 200:
                                info = info_resp.json().get('response', {})
                                model = info.get('product', 'UCM')
                                firmware = info.get('prog_version', 'unknown')
                            
                            return True, f"Successfully authenticated to Grandstream UCM\nHost: {host}:{port}\nModel: {model}\nFirmware: {firmware}"
                        else:
                            return False, "Authentication failed: Invalid credentials"
                else:
                    return False, "No challenge received"
            else:
                return False, f"HTTP {challenge_resp.status_code}"
        else:
            # IP Phone - basic auth
            response = session.get(
                f"{base_url}/cgi-bin/config",
                auth=(username, password),
                timeout=15
            )
            
            if response.status_code == 200:
                return True, f"Successfully authenticated to Grandstream Phone\nHost: {host}:{port}\nWeb interface accessible"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            else:
                return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Grandstream error: {e}"

