# SSH Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "SSH (Protocol)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "22"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "auth_type", "type": "combo", "label": "Authentication Type",
     "options": ["Password", "Private Key", "Private Key + Password"]},
    {"name": "password", "type": "password", "label": "Password / Key Passphrase"},
    {"name": "private_key", "type": "file", "label": "Private Key File", "filter": "Key Files (*.pem *.key id_rsa id_ed25519);;All Files (*)"},
    {"name": "known_hosts", "type": "file", "label": "Known Hosts File", "filter": "Known Hosts (known_hosts);;All Files (*)"},
    {"name": "verify_host_key", "type": "checkbox", "label": "Verify Host Key"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "root / root, admin / admin, ubuntu / ubuntu, ec2-user / (key)"},
]


def authenticate(form_data):
    """
    Attempt to authenticate via SSH.
    
    Args:
        form_data (dict): Form field values
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        import paramiko
    except ImportError:
        return False, "paramiko package not installed. Run: pip install paramiko"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    username = form_data.get('username', '').strip()
    auth_type = form_data.get('auth_type', 'Password')
    password = form_data.get('password', '')
    private_key_path = form_data.get('private_key', '').strip()
    known_hosts = form_data.get('known_hosts', '').strip()
    verify_host_key = form_data.get('verify_host_key', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        client = paramiko.SSHClient()
        
        # Host key verification
        if verify_host_key:
            if known_hosts:
                client.load_host_keys(known_hosts)
            else:
                client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.RejectPolicy())
        else:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        port_num = int(port) if port else 22
        
        # Prepare authentication
        connect_kwargs = {
            'hostname': host,
            'port': port_num,
            'username': username,
            'timeout': 10,
            'allow_agent': False,
            'look_for_keys': False,
        }
        
        if auth_type == "Password":
            connect_kwargs['password'] = password
        elif auth_type == "Private Key":
            if not private_key_path:
                return False, "Private key file is required for key-based authentication"
            # Try to load the key
            try:
                pkey = paramiko.RSAKey.from_private_key_file(private_key_path)
            except paramiko.ssh_exception.PasswordRequiredException:
                return False, "Private key requires a passphrase - use 'Private Key + Password'"
            except:
                try:
                    pkey = paramiko.Ed25519Key.from_private_key_file(private_key_path)
                except:
                    try:
                        pkey = paramiko.ECDSAKey.from_private_key_file(private_key_path)
                    except:
                        pkey = paramiko.DSSKey.from_private_key_file(private_key_path)
            connect_kwargs['pkey'] = pkey
        elif auth_type == "Private Key + Password":
            if not private_key_path:
                return False, "Private key file is required"
            try:
                pkey = paramiko.RSAKey.from_private_key_file(private_key_path, password=password)
            except:
                try:
                    pkey = paramiko.Ed25519Key.from_private_key_file(private_key_path, password=password)
                except:
                    try:
                        pkey = paramiko.ECDSAKey.from_private_key_file(private_key_path, password=password)
                    except:
                        pkey = paramiko.DSSKey.from_private_key_file(private_key_path, password=password)
            connect_kwargs['pkey'] = pkey
        
        # Connect
        client.connect(**connect_kwargs)
        
        # Get some info
        transport = client.get_transport()
        remote_version = transport.remote_version if transport else "unknown"
        
        # Run a simple command to verify
        stdin, stdout, stderr = client.exec_command('echo "auth_test"')
        output = stdout.read().decode().strip()
        
        client.close()
        
        if output == "auth_test":
            return True, f"Successfully authenticated to SSH server at {host}:{port_num}\nServer version: {remote_version}"
        else:
            return True, f"Authenticated but command test gave unexpected output: {output}"
            
    except paramiko.AuthenticationException:
        return False, "Authentication failed: Invalid credentials"
    except paramiko.SSHException as e:
        return False, f"SSH error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

