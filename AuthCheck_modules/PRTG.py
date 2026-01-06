# PRTG Network Monitor Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "PRTG Network Monitor (Monitoring)"

form_fields = [
    {"name": "url", "type": "text", "label": "PRTG URL"},
    {"name": "username", "type": "text", "label": "Username", "default": "prtgadmin"},
    {"name": "passhash", "type": "password", "label": "Passhash"},
    {"name": "password", "type": "password", "label": "Password (Alternative)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: prtgadmin/prtgadmin. Passhash from Setup > Account Settings > My Account."},
]


def authenticate(form_data):
    """Attempt to authenticate to PRTG."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    url = form_data.get('url', '').strip()
    username = form_data.get('username', '').strip()
    passhash = form_data.get('passhash', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not url:
        return False, "PRTG URL is required"
    if not username:
        return False, "Username is required"
    if not passhash and not password:
        return False, "Passhash or Password is required"
    
    if not url.startswith('http'):
        url = f"https://{url}"
    url = url.rstrip('/')
    
    try:
        # Build auth params
        if passhash:
            auth_params = f"username={username}&passhash={passhash}"
        else:
            auth_params = f"username={username}&password={password}"
        
        # Get status
        response = requests.get(
            f"{url}/api/getstatus.json?{auth_params}",
            verify=verify_ssl,
            timeout=15
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
            except:
                return False, "Invalid response from PRTG"
            
            version = data.get('Version', 'unknown')
            sensors = data.get('Sensors', 'unknown')
            
            # Get sensor details
            sensors_resp = requests.get(
                f"{url}/api/table.json?{auth_params}&content=sensors&columns=objid,device,sensor,status",
                verify=verify_ssl,
                timeout=10
            )
            sensor_count = 0
            warning_count = 0
            down_count = 0
            if sensors_resp.status_code == 200:
                sensor_data = sensors_resp.json().get('sensors', [])
                sensor_count = len(sensor_data)
                for s in sensor_data:
                    status = s.get('status_raw', 0)
                    if status == 4:  # Warning
                        warning_count += 1
                    elif status == 5:  # Down
                        down_count += 1
            
            return True, f"Successfully authenticated to PRTG\nVersion: {version}\nSensors: {sensor_count}\nWarning: {warning_count}\nDown: {down_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"PRTG error: {e}"

