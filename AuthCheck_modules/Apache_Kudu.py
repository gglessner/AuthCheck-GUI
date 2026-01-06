# Apache Kudu Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Kudu (BigData)"

form_fields = [
    {"name": "master_host", "type": "text", "label": "Master Host", "default": "localhost"},
    {"name": "master_port", "type": "text", "label": "Master Port", "default": "7051"},
    {"name": "admin_port", "type": "text", "label": "Admin Web Port", "default": "8051",
     "port_toggle": "use_https", "tls_port": "8051", "non_tls_port": "8051"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS (Admin UI)"},
    {"name": "require_auth", "type": "checkbox", "label": "Require Authentication"},
    {"name": "sasl_protocol", "type": "combo", "label": "SASL Protocol",
     "options": ["PLAIN", "GSSAPI"]},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Master: 7051, Admin: 8051 (TLS/non-TLS same). kudu/hostname@REALM"},
]


def authenticate(form_data):
    """
    Attempt to connect to Apache Kudu.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    master_host = form_data.get('master_host', '').strip()
    admin_port = form_data.get('admin_port', '').strip()
    use_https = form_data.get('use_https', False)
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not master_host:
        return False, "Master Host is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = admin_port if admin_port else "8051"
        base_url = f"{scheme}://{master_host}:{port_num}"
        
        # Get master status via web UI
        url = f"{base_url}/api/v1/masters"
        response = requests.get(url, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            masters = data.get('masters', [])
            
            # Get table count
            tables_url = f"{base_url}/api/v1/tables"
            tables_response = requests.get(tables_url, verify=verify_ssl, timeout=10)
            table_count = 0
            if tables_response.status_code == 200:
                table_count = len(tables_response.json().get('tables', []))
            
            master_info = []
            for m in masters:
                role = m.get('role', 'unknown')
                addr = m.get('registration', {}).get('rpc_addresses', [{}])[0].get('host', 'unknown')
                master_info.append(f"{addr}({role})")
            
            return True, f"Successfully connected to Apache Kudu\nMasters: {', '.join(master_info)}\nTables: {table_count}"
        elif response.status_code == 401:
            return False, "Authentication required"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Kudu error: {e}"

