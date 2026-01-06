# Beanstalkd Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Beanstalkd (MQ)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "11300"},
    {"name": "tube", "type": "text", "label": "Tube", "default": "default"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default port: 11300. No built-in auth (network-level security)"},
]


def authenticate(form_data):
    """
    Attempt to connect to Beanstalkd.
    Note: Beanstalkd has no built-in authentication - relies on network security.
    """
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    tube = form_data.get('tube', 'default').strip()
    
    if not host:
        return False, "Host is required"
    if not port:
        return False, "Port is required"
    
    try:
        import greenstalk
    except ImportError:
        try:
            import socket
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, int(port)))
            
            # Send stats command
            sock.send(b"stats\r\n")
            response = sock.recv(4096).decode('utf-8', errors='ignore')
            sock.close()
            
            if "OK" in response:
                lines = response.split('\n')
                stats = {}
                for line in lines:
                    if ':' in line:
                        key, val = line.split(':', 1)
                        stats[key.strip()] = val.strip()
                
                version = stats.get('version', 'unknown')
                jobs = stats.get('current-jobs-ready', '0')
                return True, f"Successfully connected to Beanstalkd {version} at {host}:{port}\nJobs ready: {jobs}"
            else:
                return False, f"Unexpected response: {response[:100]}"
                
        except Exception as e:
            return False, f"Socket error: {e}"
    
    try:
        client = greenstalk.Client((host, int(port)), watch=tube)
        stats = client.stats()
        client.close()
        
        version = stats.get('version', 'unknown')
        jobs = stats.get('current-jobs-ready', 0)
        return True, f"Successfully connected to Beanstalkd {version} at {host}:{port}\nJobs ready: {jobs}"
        
    except Exception as e:
        return False, f"Beanstalkd error: {e}"

