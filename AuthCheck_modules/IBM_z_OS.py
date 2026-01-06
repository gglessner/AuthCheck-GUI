# IBM z/OS (Mainframe) Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "IBM z/OS (Mainframe)"

form_fields = [
    {"name": "host", "type": "text", "label": "z/OS Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "23"},
    {"name": "username", "type": "text", "label": "TSO User ID"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "protocol", "type": "combo", "label": "Protocol", "options": ["TN3270", "SSH", "z/OSMF REST"], "default": "z/OSMF REST"},
    {"name": "zosmf_port", "type": "text", "label": "z/OSMF Port (REST)", "default": "443"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TSO User ID (7 char max). z/OSMF REST on port 443. RACF/Top Secret/ACF2 for security."},
]


def authenticate(form_data):
    """Attempt to authenticate to IBM z/OS."""
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '23').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    protocol = form_data.get('protocol', 'z/OSMF REST')
    zosmf_port = form_data.get('zosmf_port', '443').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "z/OS Host is required"
    if not username:
        return False, "TSO User ID is required"
    
    if protocol == "z/OSMF REST":
        try:
            import requests
        except ImportError:
            return False, "requests package not installed"
        
        try:
            base_url = f"https://{host}:{zosmf_port}"
            
            auth = (username, password)
            headers = {
                'Content-Type': 'application/json',
                'X-CSRF-ZOSMF-HEADER': ''
            }
            
            # Get z/OSMF info
            response = requests.get(f"{base_url}/zosmf/info",
                                   auth=auth, headers=headers,
                                   verify=verify_ssl, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                zosmf_version = data.get('zosmf_version', 'unknown')
                zosmf_hostname = data.get('zosmf_hostname', 'unknown')
                zos_version = data.get('zos_version', 'unknown')
                
                # Get system info
                sys_resp = requests.get(f"{base_url}/zosmf/resttopology/systems",
                                       auth=auth, headers=headers,
                                       verify=verify_ssl, timeout=15)
                system_info = ""
                if sys_resp.status_code == 200:
                    systems = sys_resp.json().get('items', [])
                    if systems:
                        system_info = f"\nSystems: {len(systems)}"
                
                return True, f"Successfully authenticated to z/OS via z/OSMF\nHost: {zosmf_hostname}\nz/OS: {zos_version}\nz/OSMF: {zosmf_version}{system_info}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            elif response.status_code == 403:
                return False, "Authentication failed: User not authorized for z/OSMF"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:200]}"
                
        except Exception as e:
            return False, f"z/OSMF error: {e}"
    
    elif protocol == "SSH":
        try:
            import paramiko
        except ImportError:
            return False, "paramiko package not installed. Run: pip install paramiko"
        
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            client.connect(
                hostname=host,
                port=int(port) if port != '23' else 22,
                username=username,
                password=password,
                timeout=15,
                allow_agent=False,
                look_for_keys=False
            )
            
            # Try to execute a simple command
            stdin, stdout, stderr = client.exec_command('uname -a', timeout=10)
            output = stdout.read().decode().strip()
            
            client.close()
            return True, f"Successfully authenticated to z/OS via SSH\nHost: {host}\nOutput: {output[:100]}"
            
        except paramiko.AuthenticationException:
            return False, "Authentication failed: Invalid credentials"
        except Exception as e:
            return False, f"SSH error: {e}"
    
    else:  # TN3270
        return False, "TN3270 authentication requires a 3270 emulator library. Consider using z/OSMF REST or SSH."

