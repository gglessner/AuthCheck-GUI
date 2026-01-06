# Avaya Communication Manager Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Avaya Communication Manager (PBX)"

form_fields = [
    {"name": "host", "type": "text", "label": "Avaya CM Host"},
    {"name": "port", "type": "text", "label": "SSH Port", "default": "5022"},
    {"name": "username", "type": "text", "label": "Username", "default": "dadmin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: dadmin/dadmin01, craft/crftpw. SAT port 5022 or 5023."},
]


def authenticate(form_data):
    """Attempt to authenticate to Avaya Communication Manager."""
    try:
        import paramiko
    except ImportError:
        return False, "paramiko package not installed. Run: pip install paramiko"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '5022').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    if not host:
        return False, "Avaya CM Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        client.connect(
            hostname=host,
            port=int(port),
            username=username,
            password=password,
            timeout=15,
            look_for_keys=False,
            allow_agent=False
        )
        
        # Try to get system info
        stdin, stdout, stderr = client.exec_command('display system-parameters customer-options')
        output = stdout.read().decode('utf-8', errors='ignore')
        
        # Try version
        stdin2, stdout2, stderr2 = client.exec_command('display system-parameters system-version')
        version_output = stdout2.read().decode('utf-8', errors='ignore')
        
        client.close()
        
        # Parse version if available
        version = 'unknown'
        if version_output:
            import re
            ver_match = re.search(r'Version\s+(\S+)', version_output)
            if ver_match:
                version = ver_match.group(1)
        
        return True, f"Successfully authenticated to Avaya CM\nHost: {host}:{port}\nUser: {username}\nVersion: {version}\nSAT Access: Granted"
        
    except paramiko.AuthenticationException:
        return False, "Authentication failed: Invalid credentials"
    except paramiko.SSHException as e:
        return False, f"SSH error: {e}"
    except Exception as e:
        return False, f"Avaya CM error: {e}"

