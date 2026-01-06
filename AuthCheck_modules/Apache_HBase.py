# Apache HBase Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache HBase (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Thrift Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Thrift Port", "default": "9090"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS (REST)"},
    {"name": "rest_port", "type": "text", "label": "REST Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "8085", "non_tls_port": "8080"},
    {"name": "protocol", "type": "combo", "label": "Protocol",
     "options": ["Thrift", "REST API"]},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Kerberos"]},
    {"name": "kerberos_principal", "type": "text", "label": "Kerberos Principal"},
    {"name": "keytab_file", "type": "file", "label": "Keytab File", "filter": "Keytab Files (*.keytab);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Thrift: 9090, REST TLS: 8085, Non-TLS: 8080. hbase/hostname@REALM"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache HBase.
    """
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    rest_port = form_data.get('rest_port', '').strip()
    use_https = form_data.get('use_https', False)
    protocol = form_data.get('protocol', 'Thrift')
    
    if not host:
        return False, "Host is required"
    
    if protocol == "Thrift":
        try:
            import happybase
        except ImportError:
            return False, "happybase package not installed. Run: pip install happybase"
        
        try:
            port_num = int(port) if port else 9090
            connection = happybase.Connection(host, port=port_num, timeout=10000)
            
            # Try to list tables to verify connection
            tables = connection.tables()
            connection.close()
            
            return True, f"Successfully connected to HBase at {host}:{port_num} via Thrift\nTables: {len(tables)}"
            
        except Exception as e:
            return False, f"HBase Thrift error: {e}"
    
    else:  # REST API
        try:
            import requests
        except ImportError:
            return False, "requests package not installed. Run: pip install requests"
        
        try:
            scheme = "https" if use_https else "http"
            rest_port_num = rest_port if rest_port else "8080"
            url = f"{scheme}://{host}:{rest_port_num}/version/cluster"
            
            response = requests.get(url, timeout=10, verify=False)
            
            if response.status_code == 200:
                return True, f"Successfully connected to HBase REST API at {host}:{rest_port_num}\n{response.text[:100]}"
            elif response.status_code == 401:
                return False, "Authentication failed: Unauthorized"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:200]}"
                
        except Exception as e:
            return False, f"HBase REST error: {e}"

