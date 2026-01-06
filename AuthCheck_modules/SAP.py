# SAP ERP/S4HANA Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "SAP ERP/S4HANA (ERP)"

form_fields = [
    {"name": "host", "type": "text", "label": "SAP Host"},
    {"name": "system_number", "type": "text", "label": "System Number", "default": "00"},
    {"name": "client", "type": "text", "label": "Client", "default": "100"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "protocol", "type": "combo", "label": "Protocol", "options": ["RFC (PyRFC)", "OData/REST"], "default": "OData/REST"},
    {"name": "port", "type": "text", "label": "HTTP Port (OData)", "default": "8000",
     "port_toggle": "use_https", "tls_port": "44300", "non_tls_port": "8000"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 44300, Non-TLS: 8000. Client 000/001. DDIC / 19920706."},
]


def authenticate(form_data):
    """Attempt to authenticate to SAP ERP/S4HANA."""
    host = form_data.get('host', '').strip()
    system_number = form_data.get('system_number', '00').strip()
    client = form_data.get('client', '100').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    protocol = form_data.get('protocol', 'OData/REST')
    port = form_data.get('port', '8000').strip()
    use_https = form_data.get('use_https', False)
    
    if not host:
        return False, "SAP Host is required"
    if not username:
        return False, "Username is required"
    
    if protocol == "RFC (PyRFC)":
        try:
            from pyrfc import Connection
        except ImportError:
            return False, "pyrfc package not installed. Run: pip install pyrfc (requires SAP NW RFC SDK)"
        
        try:
            conn = Connection(
                ashost=host,
                sysnr=system_number,
                client=client,
                user=username,
                passwd=password
            )
            
            # Get system info
            result = conn.call('RFC_SYSTEM_INFO')
            
            sys_info = result.get('RFCSI_EXPORT', {})
            release = sys_info.get('RFCSYSID', 'unknown')
            host_name = sys_info.get('RFCHOST', 'unknown')
            db_system = sys_info.get('RFCDBSYS', 'unknown')
            
            conn.close()
            
            return True, f"Successfully authenticated to SAP via RFC\nSystem: {release}\nHost: {host_name}\nClient: {client}\nDB: {db_system}"
            
        except Exception as e:
            return False, f"SAP RFC error: {e}"
    else:
        # OData/REST
        try:
            import requests
            from requests.auth import HTTPBasicAuth
        except ImportError:
            return False, "requests package not installed"
        
        try:
            scheme = "https" if use_https else "http"
            base_url = f"{scheme}://{host}:{port}"
            
            auth = HTTPBasicAuth(username, password)
            headers = {
                'Accept': 'application/json',
                'sap-client': client
            }
            
            # Try to access OData service
            response = requests.get(f"{base_url}/sap/opu/odata/sap/API_BUSINESS_PARTNER",
                                   auth=auth, headers=headers, timeout=15, verify=False)
            
            if response.status_code == 200:
                return True, f"Successfully authenticated to SAP via OData\nHost: {host}\nClient: {client}\nUser: {username}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            elif response.status_code == 403:
                return False, "Authentication failed: User not authorized"
            elif response.status_code == 404:
                # Service might not exist, try simpler endpoint
                response2 = requests.get(f"{base_url}/sap/bc/ping",
                                        auth=auth, headers=headers, timeout=15, verify=False)
                if response2.status_code in [200, 204]:
                    return True, f"Successfully authenticated to SAP\nHost: {host}\nClient: {client}\nUser: {username}"
                else:
                    return False, f"SAP endpoint not found. Check host and port."
            else:
                return False, f"HTTP {response.status_code}: {response.text[:200]}"
                
        except Exception as e:
            return False, f"SAP OData error: {e}"

