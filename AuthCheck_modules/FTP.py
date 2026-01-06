# FTP/SFTP Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "FTP / SFTP (Protocol)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "21",
     "port_toggle": "protocol", "tls_port": "990", "non_tls_port": "21"},
    {"name": "protocol", "type": "combo", "label": "Protocol",
     "options": ["FTP", "FTPS (Explicit)", "FTPS (Implicit)", "SFTP"]},
    {"name": "username", "type": "text", "label": "Username", "default": "anonymous"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "private_key", "type": "file", "label": "Private Key (SFTP)", "filter": "Key Files (*.pem *.key id_rsa);;All Files (*)"},
    {"name": "key_passphrase", "type": "password", "label": "Key Passphrase"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "FTP: 21, FTPS Implicit: 990, SFTP: 22. anonymous / anonymous@"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to FTP/SFTP server.
    """
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    protocol = form_data.get('protocol', 'FTP')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    private_key = form_data.get('private_key', '').strip()
    key_passphrase = form_data.get('key_passphrase', '')
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    if protocol == "SFTP":
        try:
            import paramiko
        except ImportError:
            return False, "paramiko package not installed. Run: pip install paramiko"
        
        try:
            port_num = int(port) if port else 22
            
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_kwargs = {
                'hostname': host,
                'port': port_num,
                'username': username,
                'timeout': 10,
                'allow_agent': False,
                'look_for_keys': False,
            }
            
            if private_key:
                try:
                    pkey = paramiko.RSAKey.from_private_key_file(
                        private_key, 
                        password=key_passphrase if key_passphrase else None
                    )
                except:
                    try:
                        pkey = paramiko.Ed25519Key.from_private_key_file(
                            private_key,
                            password=key_passphrase if key_passphrase else None
                        )
                    except:
                        pkey = paramiko.ECDSAKey.from_private_key_file(
                            private_key,
                            password=key_passphrase if key_passphrase else None
                        )
                connect_kwargs['pkey'] = pkey
            else:
                connect_kwargs['password'] = password
            
            client.connect(**connect_kwargs)
            sftp = client.open_sftp()
            
            # List root to verify access
            root_contents = sftp.listdir('.')
            
            sftp.close()
            client.close()
            
            return True, f"Successfully authenticated to SFTP at {host}:{port_num}\nCurrent directory has {len(root_contents)} items"
            
        except paramiko.AuthenticationException:
            return False, "Authentication failed: Invalid credentials"
        except Exception as e:
            return False, f"SFTP error: {e}"
    
    else:  # FTP/FTPS
        try:
            from ftplib import FTP, FTP_TLS
        except ImportError:
            return False, "ftplib not available"
        
        try:
            port_num = int(port) if port else 21
            
            if protocol == "FTPS (Implicit)":
                import ssl
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                ftp = FTP_TLS(context=context)
                ftp.connect(host, port_num, timeout=10)
            elif protocol == "FTPS (Explicit)":
                ftp = FTP_TLS()
                ftp.connect(host, port_num, timeout=10)
                ftp.auth()
                ftp.prot_p()
            else:
                ftp = FTP()
                ftp.connect(host, port_num, timeout=10)
            
            ftp.login(username, password)
            
            # Get welcome message and current directory
            welcome = ftp.getwelcome()
            pwd = ftp.pwd()
            
            ftp.quit()
            
            return True, f"Successfully authenticated to {protocol} at {host}:{port_num}\nDirectory: {pwd}\n{welcome}"
            
        except Exception as e:
            error_msg = str(e)
            if "530" in error_msg or "Login" in error_msg:
                return False, f"Authentication failed: {e}"
            return False, f"FTP error: {e}"

