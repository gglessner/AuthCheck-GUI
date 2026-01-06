# OpenWrt Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "OpenWrt / LEDE (Wireless)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "192.168.1.1"},
    {"name": "port", "type": "text", "label": "Port", "default": "443",
     "port_toggle": "use_https", "tls_port": "443", "non_tls_port": "80"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_method", "type": "combo", "label": "Auth Method",
     "options": ["LuCI Web", "ubus RPC", "SSH"]},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "root / (blank or set during setup). LuCI default port: 80/443"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to OpenWrt.
    """
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_https = form_data.get('use_https', False)
    auth_method = form_data.get('auth_method', 'LuCI Web')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    scheme = "https" if use_https else "http"
    base_url = f"{scheme}://{host}:{port}"
    
    if auth_method == "SSH":
        try:
            import paramiko
        except ImportError:
            return False, "paramiko package not installed. Run: pip install paramiko"
        
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, port=22, username=username, password=password, timeout=10)
            
            stdin, stdout, stderr = client.exec_command("cat /etc/openwrt_release")
            output = stdout.read().decode('utf-8')
            client.close()
            
            version = "unknown"
            for line in output.split('\n'):
                if 'DISTRIB_RELEASE' in line:
                    version = line.split('=')[1].strip().strip("'\"")
                    break
            
            return True, f"Successfully authenticated to OpenWrt via SSH\nVersion: {version}"
            
        except Exception as e:
            return False, f"SSH error: {e}"
    
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        if auth_method == "ubus RPC":
            # ubus JSON-RPC
            rpc_url = f"{base_url}/ubus"
            
            login_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "call",
                "params": ["00000000000000000000000000000000", "session", "login", 
                          {"username": username, "password": password}]
            }
            
            response = session.post(rpc_url, json=login_data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result') and len(result['result']) > 1:
                    session_data = result['result'][1]
                    if session_data.get('ubus_rpc_session'):
                        return True, f"Successfully authenticated to OpenWrt via ubus at {host}"
                return False, "Authentication failed: Invalid credentials"
                
        else:  # LuCI Web
            # LuCI login
            login_url = f"{base_url}/cgi-bin/luci"
            
            # Get login page first
            session.get(login_url, timeout=10)
            
            login_data = {
                "luci_username": username,
                "luci_password": password
            }
            
            response = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
            
            if response.status_code == 200:
                if "logout" in response.text.lower() or "status" in response.text.lower():
                    # Try to get version
                    version = "unknown"
                    if "openwrt" in response.text.lower():
                        import re
                        match = re.search(r'OpenWrt\s+([0-9.]+)', response.text)
                        if match:
                            version = match.group(1)
                    
                    return True, f"Successfully authenticated to OpenWrt LuCI at {host}\nVersion: {version}"
                elif "invalid" in response.text.lower() or "failed" in response.text.lower():
                    return False, "Authentication failed: Invalid credentials"
            
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"OpenWrt error: {e}"

