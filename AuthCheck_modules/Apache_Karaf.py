# Apache Karaf Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Karaf (Middleware)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "ssh_port", "type": "text", "label": "SSH Port", "default": "8101"},
    {"name": "http_port", "type": "text", "label": "HTTP Port", "default": "8181"},
    {"name": "use_ssh", "type": "checkbox", "label": "Use SSH", "default": True},
    {"name": "username", "type": "text", "label": "Username", "default": "karaf"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "karaf / karaf (default)"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Karaf.
    """
    host = form_data.get('host', '').strip()
    ssh_port = form_data.get('ssh_port', '').strip()
    http_port = form_data.get('http_port', '').strip()
    use_ssh = form_data.get('use_ssh', True)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    if use_ssh:
        try:
            import paramiko
        except ImportError:
            return False, "paramiko package not installed. Run: pip install paramiko"
        
        try:
            port_num = int(ssh_port) if ssh_port else 8101
            
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            client.connect(
                hostname=host,
                port=port_num,
                username=username,
                password=password,
                timeout=10,
                allow_agent=False,
                look_for_keys=False
            )
            
            # Execute a command
            stdin, stdout, stderr = client.exec_command("version")
            version = stdout.read().decode().strip()
            
            # Get bundles
            stdin, stdout, stderr = client.exec_command("bundle:list | wc -l")
            bundle_count = stdout.read().decode().strip()
            
            client.close()
            
            return True, f"Successfully authenticated to Apache Karaf via SSH\nVersion: {version}\nBundles: {bundle_count}"
            
        except paramiko.AuthenticationException:
            return False, "SSH authentication failed: Invalid credentials"
        except Exception as e:
            return False, f"Karaf SSH error: {e}"
    else:
        try:
            import requests
            from requests.auth import HTTPBasicAuth
        except ImportError:
            return False, "requests package not installed. Run: pip install requests"
        
        try:
            port_num = http_port if http_port else "8181"
            base_url = f"http://{host}:{port_num}/system/console"
            
            auth = HTTPBasicAuth(username, password)
            response = requests.get(f"{base_url}/bundles.json", auth=auth, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                bundles = data.get('data', [])
                return True, f"Successfully authenticated to Apache Karaf Web Console\nBundles: {len(bundles)}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Karaf HTTP error: {e}"

