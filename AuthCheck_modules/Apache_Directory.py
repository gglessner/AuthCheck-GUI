# Apache Directory Server Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Directory Server (IAM)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "10389",
     "port_toggle": "use_ssl", "tls_port": "10636", "non_tls_port": "10389"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use LDAPS"},
    {"name": "start_tls", "type": "checkbox", "label": "Use StartTLS"},
    {"name": "bind_dn", "type": "text", "label": "Bind DN", "default": "uid=admin,ou=system"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "base_dn", "type": "text", "label": "Base DN", "default": "dc=example,dc=com"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "LDAPS: 10636, LDAP: 10389. admin / secret"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Directory Server.
    """
    try:
        import ldap3
    except ImportError:
        return False, "ldap3 package not installed. Run: pip install ldap3"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_ssl = form_data.get('use_ssl', False)
    start_tls = form_data.get('start_tls', False)
    bind_dn = form_data.get('bind_dn', '').strip()
    password = form_data.get('password', '')
    base_dn = form_data.get('base_dn', '').strip()
    
    if not host:
        return False, "Host is required"
    if not bind_dn:
        return False, "Bind DN is required"
    
    try:
        port_num = int(port) if port else (10636 if use_ssl else 10389)
        
        server = ldap3.Server(host, port=port_num, use_ssl=use_ssl, get_info=ldap3.ALL)
        
        conn = ldap3.Connection(server, user=bind_dn, password=password, auto_bind=False)
        
        if start_tls and not use_ssl:
            conn.open()
            conn.start_tls()
        
        if conn.bind():
            # Get server info
            vendor = server.info.vendor_name if server.info else 'Apache Directory Server'
            version = server.info.vendor_version if server.info else 'unknown'
            naming_contexts = server.info.naming_contexts if server.info else []
            
            # Count entries if base_dn provided
            entry_count = 0
            if base_dn:
                conn.search(base_dn, '(objectClass=*)', search_scope=ldap3.SUBTREE, size_limit=1000)
                entry_count = len(conn.entries)
            
            conn.unbind()
            
            return True, f"Successfully authenticated to Apache Directory Server\nVendor: {vendor} {version}\nNaming Contexts: {naming_contexts}\nEntries in {base_dn}: {entry_count}"
        else:
            return False, f"Bind failed: {conn.result.get('description', 'Unknown error')}"
            
    except Exception as e:
        error_msg = str(e)
        if "invalidCredentials" in error_msg:
            return False, "Authentication failed: Invalid credentials"
        return False, f"Directory Server error: {e}"

