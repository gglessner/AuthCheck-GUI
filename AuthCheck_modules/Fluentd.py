# Fluentd Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Fluentd (Logging)"

form_fields = [
    {"name": "host", "type": "text", "label": "Fluentd Host"},
    {"name": "monitor_port", "type": "text", "label": "Monitor Agent Port", "default": "24220",
     "port_toggle": "use_ssl", "tls_port": "24220", "non_tls_port": "24220"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Monitor: 24220, Forward: 24224 (TLS/non-TLS same). Plugin required."},
]


def authenticate(form_data):
    """Attempt to authenticate to Fluentd."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    monitor_port = form_data.get('monitor_port', '24220').strip()
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "Fluentd Host is required"
    
    try:
        scheme = "https" if use_ssl else "http"
        base_url = f"{scheme}://{host}:{monitor_port}"
        
        # Get plugins info
        response = requests.get(
            f"{base_url}/api/plugins.json",
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            plugins = data.get('plugins', [])
            
            # Categorize plugins
            inputs = sum(1 for p in plugins if p.get('type') == 'input')
            outputs = sum(1 for p in plugins if p.get('type') == 'output')
            filters = sum(1 for p in plugins if p.get('type') == 'filter')
            
            # Get config
            config_resp = requests.get(
                f"{base_url}/api/config.json",
                timeout=10
            )
            config_info = ""
            if config_resp.status_code == 200:
                config = config_resp.json()
                config_info = f"\nPid: {config.get('pid', 'unknown')}"
            
            return True, f"Successfully connected to Fluentd\nHost: {host}:{monitor_port}\nPlugins: {len(plugins)}\nInputs: {inputs}, Outputs: {outputs}, Filters: {filters}{config_info}"
        else:
            # Try basic TCP connection on forward port
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, 24224))
            sock.close()
            
            if result == 0:
                return True, f"Successfully connected to Fluentd Forward Input\nHost: {host}:24224\nNote: Enable monitor_agent plugin for detailed info"
            else:
                return False, f"Cannot connect to Fluentd on {host}"
            
    except Exception as e:
        return False, f"Fluentd error: {e}"

