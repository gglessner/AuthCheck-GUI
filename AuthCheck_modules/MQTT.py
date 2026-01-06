# MQTT Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "MQTT / Mosquitto (MQ)"

form_fields = [
    {"name": "host", "type": "text", "label": "Broker Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "1883",
     "port_toggle": "use_tls", "tls_port": "8883", "non_tls_port": "1883"},
    {"name": "use_tls", "type": "checkbox", "label": "Enable TLS"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "client_id", "type": "text", "label": "Client ID"},
    {"name": "tls_ca", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "tls_cert", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "tls_key", "type": "file", "label": "Client Key", "filter": "Key Files (*.pem *.key);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8883, Non-TLS: 1883. Mosquitto: mosquitto / mosquitto, admin / admin"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to MQTT broker.
    """
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        return False, "paho-mqtt package not installed. Run: pip install paho-mqtt"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    use_tls = form_data.get('use_tls', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    client_id = form_data.get('client_id', '').strip()
    tls_ca = form_data.get('tls_ca', '').strip()
    tls_cert = form_data.get('tls_cert', '').strip()
    tls_key = form_data.get('tls_key', '').strip()
    
    if not host:
        return False, "Broker Host is required"
    
    result = {'connected': False, 'error': None}
    
    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            result['connected'] = True
        else:
            error_codes = {
                1: "Incorrect protocol version",
                2: "Invalid client identifier",
                3: "Server unavailable",
                4: "Bad username or password",
                5: "Not authorized",
            }
            result['error'] = error_codes.get(rc, f"Connection refused (code {rc})")
    
    try:
        # Use callback API version 2 if available
        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id if client_id else None)
        except (AttributeError, TypeError):
            client = mqtt.Client(client_id=client_id if client_id else None)
        
        client.on_connect = on_connect
        
        if username:
            client.username_pw_set(username, password)
        
        port_num = int(port) if port else (8883 if use_tls else 1883)
        
        if use_tls:
            import ssl
            if tls_ca or tls_cert:
                client.tls_set(
                    ca_certs=tls_ca if tls_ca else None,
                    certfile=tls_cert if tls_cert else None,
                    keyfile=tls_key if tls_key else None,
                    cert_reqs=ssl.CERT_REQUIRED if tls_ca else ssl.CERT_NONE
                )
            else:
                client.tls_set(cert_reqs=ssl.CERT_NONE)
            client.tls_insecure_set(True)
        
        client.connect(host, port_num, keepalive=10)
        client.loop_start()
        
        # Wait for connection
        import time
        timeout = 10
        start = time.time()
        while not result['connected'] and result['error'] is None and (time.time() - start) < timeout:
            time.sleep(0.1)
        
        client.loop_stop()
        client.disconnect()
        
        if result['connected']:
            return True, f"Successfully authenticated to MQTT broker at {host}:{port_num}"
        elif result['error']:
            return False, f"Authentication failed: {result['error']}"
        else:
            return False, "Connection timed out"
            
    except Exception as e:
        return False, f"MQTT error: {e}"

