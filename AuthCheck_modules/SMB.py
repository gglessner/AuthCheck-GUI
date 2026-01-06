# SMB/CIFS Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "SMB / CIFS (Protocol)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "445",
     "port_toggle": "use_ntlm", "tls_port": "445", "non_tls_port": "445"},
    {"name": "share", "type": "text", "label": "Share Name"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "domain", "type": "text", "label": "Domain"},
    {"name": "use_ntlm", "type": "checkbox", "label": "Use NTLMv2", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 445 (SMB Direct). guest / (empty), DOMAIN\\user format."},
]


def authenticate(form_data):
    """
    Attempt to authenticate to SMB/CIFS share.
    """
    try:
        from smb.SMBConnection import SMBConnection
    except ImportError:
        return False, "pysmb package not installed. Run: pip install pysmb"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    share = form_data.get('share', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    domain = form_data.get('domain', '').strip()
    use_ntlm = form_data.get('use_ntlm', True)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        port_num = int(port) if port else 445
        
        conn = SMBConnection(
            username,
            password,
            'authcheck',
            host,
            domain=domain if domain else '',
            use_ntlm_v2=use_ntlm,
            is_direct_tcp=True
        )
        
        connected = conn.connect(host, port_num, timeout=10)
        
        if connected:
            # List shares
            shares = conn.listShares()
            share_names = [s.name for s in shares]
            
            # If a specific share was specified, try to access it
            share_info = ""
            if share:
                try:
                    files = conn.listPath(share, '/')
                    share_info = f"\nShare '{share}' accessible with {len(files)} items in root"
                except Exception as e:
                    share_info = f"\nShare '{share}' not accessible: {e}"
            
            conn.close()
            
            return True, f"Successfully authenticated to SMB at {host}:{port_num}\nAvailable shares: {share_names}{share_info}"
        else:
            return False, "Connection failed"
            
    except Exception as e:
        error_msg = str(e)
        if "STATUS_LOGON_FAILURE" in error_msg or "Authentication" in error_msg:
            return False, "Authentication failed: Invalid credentials"
        return False, f"SMB error: {e}"

