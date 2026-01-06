# Juniper Networks Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Juniper Networks (Network)"

form_fields = [
    {"name": "host", "type": "text", "label": "Device Host"},
    {"name": "port", "type": "text", "label": "NETCONF Port", "default": "830"},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "ssh_key", "type": "file", "label": "SSH Private Key", "filter": "Key Files (*.pem *.key *.pub);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "root / (set at install). NETCONF port 830, SSH port 22."},
]


def authenticate(form_data):
    """Attempt to authenticate to Juniper device."""
    try:
        import paramiko
    except ImportError:
        return False, "paramiko package not installed. Run: pip install paramiko"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '830').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    ssh_key = form_data.get('ssh_key', '').strip()
    
    if not host:
        return False, "Device Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        # Try SSH first (port 22) for basic auth test
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        connect_kwargs = {
            'hostname': host,
            'port': 22,
            'username': username,
            'timeout': 15,
            'allow_agent': False,
            'look_for_keys': False
        }
        
        if ssh_key:
            connect_kwargs['key_filename'] = ssh_key
        else:
            connect_kwargs['password'] = password
        
        ssh.connect(**connect_kwargs)
        
        # Get version info
        stdin, stdout, stderr = ssh.exec_command('show version | match "Junos:|Model:|Hostname:"')
        version_output = stdout.read().decode('utf-8').strip()
        
        # Parse output
        version = 'unknown'
        model = 'unknown'
        hostname = 'unknown'
        for line in version_output.split('\n'):
            if 'Junos:' in line:
                version = line.split('Junos:')[1].strip().split()[0]
            elif 'Model:' in line:
                model = line.split('Model:')[1].strip()
            elif 'Hostname:' in line:
                hostname = line.split('Hostname:')[1].strip()
        
        # Get interface count
        stdin, stdout, stderr = ssh.exec_command('show interfaces terse | count')
        iface_count = stdout.read().decode('utf-8').strip()
        
        ssh.close()
        
        return True, f"Successfully authenticated to Juniper\nHostname: {hostname}\nModel: {model}\nJunos: {version}\nInterfaces: {iface_count}"
        
    except paramiko.AuthenticationException:
        return False, "Authentication failed: Invalid credentials"
    except Exception as e:
        return False, f"Juniper error: {e}"

