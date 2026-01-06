# LDAP/Active Directory Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "LDAP / Active Directory (IAM)"

form_fields = [
    {"name": "host", "type": "text", "label": "Server", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "389",
     "port_toggle": "use_ssl", "tls_port": "636", "non_tls_port": "389"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use LDAPS (SSL)"},
    {"name": "use_starttls", "type": "checkbox", "label": "Use StartTLS"},
    {"name": "bind_type", "type": "combo", "label": "Bind Type",
     "options": ["Simple", "NTLM", "Kerberos (GSSAPI)"]},
    {"name": "bind_dn", "type": "text", "label": "Bind DN / Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "base_dn", "type": "text", "label": "Base DN (for search test)"},
    {"name": "verify_cert", "type": "checkbox", "label": "Verify Server Certificate"},
    {"name": "ca_cert", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "LDAPS: 636, LDAP: 389. cn=admin,dc=example,dc=com / admin"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to LDAP/Active Directory.
    
    Args:
        form_data (dict): Form field values
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        import ldap3
        from ldap3 import Server, Connection, ALL, NTLM, SASL, KERBEROS
        from ldap3.core.exceptions import LDAPException, LDAPBindError
    except ImportError:
        return False, "ldap3 package not installed. Run: pip install ldap3"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_ssl = form_data.get('use_ssl', False)
    use_starttls = form_data.get('use_starttls', False)
    bind_type = form_data.get('bind_type', 'Simple')
    bind_dn = form_data.get('bind_dn', '').strip()
    password = form_data.get('password', '')
    base_dn = form_data.get('base_dn', '').strip()
    verify_cert = form_data.get('verify_cert', False)
    ca_cert = form_data.get('ca_cert', '').strip()
    
    if not host:
        return False, "Server is required"
    if not bind_dn:
        return False, "Bind DN / Username is required"
    
    try:
        # Determine port
        if port:
            port_num = int(port)
        else:
            port_num = 636 if use_ssl else 389
        
        # Setup TLS if needed
        tls_config = None
        if use_ssl or use_starttls:
            from ldap3 import Tls
            import ssl as ssl_module
            
            tls_config = Tls(
                validate=ssl_module.CERT_REQUIRED if verify_cert else ssl_module.CERT_NONE,
                ca_certs_file=ca_cert if ca_cert else None,
            )
        
        # Create server object
        server = Server(
            host,
            port=port_num,
            use_ssl=use_ssl,
            get_info=ALL,
            tls=tls_config,
            connect_timeout=10
        )
        
        # Setup authentication
        auth_method = None
        if bind_type == "NTLM":
            auth_method = NTLM
        elif bind_type == "Kerberos (GSSAPI)":
            auth_method = SASL
            sasl_mechanism = KERBEROS
        
        # Create connection
        if bind_type == "Kerberos (GSSAPI)":
            conn = Connection(
                server,
                authentication=SASL,
                sasl_mechanism=KERBEROS,
                auto_bind=False
            )
        elif bind_type == "NTLM":
            conn = Connection(
                server,
                user=bind_dn,
                password=password,
                authentication=NTLM,
                auto_bind=False
            )
        else:  # Simple
            conn = Connection(
                server,
                user=bind_dn,
                password=password,
                auto_bind=False
            )
        
        # StartTLS if requested
        if use_starttls and not use_ssl:
            conn.open()
            if not conn.start_tls():
                return False, "StartTLS failed"
        
        # Attempt bind
        if not conn.bind():
            return False, f"Bind failed: {conn.result}"
        
        # Get server info
        server_info = []
        if server.info:
            if hasattr(server.info, 'vendor_name') and server.info.vendor_name:
                server_info.append(f"Vendor: {server.info.vendor_name}")
            if hasattr(server.info, 'vendor_version') and server.info.vendor_version:
                server_info.append(f"Version: {server.info.vendor_version}")
        
        # Try a search if base_dn provided
        search_result = ""
        if base_dn:
            conn.search(base_dn, '(objectClass=*)', attributes=['*'], size_limit=1)
            if conn.entries:
                search_result = f"\nSearch test: Found {len(conn.entries)} entry in {base_dn}"
        
        conn.unbind()
        
        info_str = "\n".join(server_info) if server_info else ""
        return True, f"Successfully authenticated to LDAP server at {host}:{port_num}\n{info_str}{search_result}"
        
    except LDAPBindError as e:
        return False, f"LDAP bind error: {e}"
    except LDAPException as e:
        return False, f"LDAP error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

