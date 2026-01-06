# Synology DSM Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Synology DSM (NAS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.100"},
    {"name": "port", "type": "text", "label": "Port", "default": "5001",
     "port_toggle": "use_https", "tls_port": "5001", "non_tls_port": "5000"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "otp_code", "type": "text", "label": "OTP Code (if 2FA)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / (set during setup). HTTP: 5000, HTTPS: 5001"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Synology DiskStation Manager.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '5001').strip()
    use_https = form_data.get('use_https', True)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    otp_code = form_data.get('otp_code', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    scheme = "https" if use_https else "http"
    base_url = f"{scheme}://{host}:{port}"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        # DSM API login
        login_url = f"{base_url}/webapi/auth.cgi"
        params = {
            "api": "SYNO.API.Auth",
            "version": "3",
            "method": "login",
            "account": username,
            "passwd": password,
            "session": "FileStation",
            "format": "sid"
        }
        
        if otp_code:
            params["otp_code"] = otp_code
        
        response = session.get(login_url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                sid = data.get("data", {}).get("sid")
                
                # Get DSM info
                info_url = f"{base_url}/webapi/entry.cgi"
                info_params = {
                    "api": "SYNO.DSM.Info",
                    "version": "2",
                    "method": "getinfo",
                    "_sid": sid
                }
                
                info_resp = session.get(info_url, params=info_params, timeout=10)
                
                model = "Synology NAS"
                dsm_version = "unknown"
                if info_resp.status_code == 200:
                    info_data = info_resp.json()
                    if info_data.get("success"):
                        model = info_data.get("data", {}).get("model", "Synology NAS")
                        dsm_version = info_data.get("data", {}).get("version_string", "unknown")
                
                # Logout
                session.get(login_url, params={
                    "api": "SYNO.API.Auth",
                    "version": "1",
                    "method": "logout",
                    "session": "FileStation"
                }, timeout=5)
                
                return True, f"Successfully authenticated to {model}\nDSM Version: {dsm_version}"
            else:
                error_code = data.get("error", {}).get("code", 0)
                if error_code == 400:
                    return False, "Authentication failed: Invalid credentials"
                elif error_code == 403:
                    return False, "Authentication failed: 2FA required"
                elif error_code == 404:
                    return False, "Authentication failed: OTP code required or invalid"
                else:
                    return False, f"Authentication failed: Error code {error_code}"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"Synology error: {e}"

