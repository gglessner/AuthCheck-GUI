# Apache Beam (Dataflow Runner) Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Beam (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Job Server Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Artifact Port", "default": "8098",
     "port_toggle": "use_ssl", "tls_port": "8098", "non_tls_port": "8098"},
    {"name": "expansion_port", "type": "text", "label": "Expansion Port", "default": "8097",
     "port_toggle": "use_ssl", "tls_port": "8097", "non_tls_port": "8097"},
    {"name": "use_ssl", "type": "checkbox", "label": "Enable SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Artifact: 8098, Expansion: 8097 (TLS/non-TLS same). No native auth."},
]


def authenticate(form_data):
    """
    Attempt to connect to Apache Beam Job Server.
    """
    import socket
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    expansion_port = form_data.get('expansion_port', '').strip()
    
    if not host:
        return False, "Job Server Host is required"
    
    try:
        port_num = int(port) if port else 8098
        exp_port = int(expansion_port) if expansion_port else 8097
        
        # Test artifact service port
        artifact_ok = False
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port_num))
            artifact_ok = (result == 0)
            sock.close()
        except:
            pass
        
        # Test expansion service port
        expansion_ok = False
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, exp_port))
            expansion_ok = (result == 0)
            sock.close()
        except:
            pass
        
        if artifact_ok or expansion_ok:
            services = []
            if artifact_ok:
                services.append(f"Artifact Service (:{port_num})")
            if expansion_ok:
                services.append(f"Expansion Service (:{exp_port})")
            
            return True, f"Apache Beam Job Server at {host}\nAvailable: {', '.join(services)}"
        else:
            return False, f"Could not connect to Beam Job Server at {host}:{port_num}"
            
    except Exception as e:
        return False, f"Beam error: {e}"

