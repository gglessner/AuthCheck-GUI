# EMQX Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "EMQX (MQ)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "mqtt_port", "type": "text", "label": "MQTT Port", "default": "1883",
     "port_toggle": "use_tls", "tls_port": "8883", "non_tls_port": "1883"},
    {"name": "ws_port", "type": "text", "label": "WebSocket Port", "default": "8083",
     "port_toggle": "use_tls", "tls_port": "8084", "non_tls_port": "8083"},
    {"name": "dashboard_port", "type": "text", "label": "Dashboard Port", "default": "18083"},
    {"name": "protocol", "type": "combo", "label": "Protocol",
     "options": ["MQTT", "WebSocket", "Dashboard API"]},
    {"name": "use_tls", "type": "checkbox", "label": "Enable TLS"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": "authcheck"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "MQTT: 1883/8883, WS: 8083/8084, Dashboard: 18083. admin / public"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to EMQX.
    """
    host = form_data.get('host', '').strip()
    mqtt_port = form_data.get('mqtt_port', '').strip()
    ws_port = form_data.get('ws_port', '').strip()
    dashboard_port = form_data.get('dashboard_port', '').strip()
    protocol = form_data.get('protocol', 'MQTT')
    use_tls = form_data.get('use_tls', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    client_id = form_data.get('client_id', 'authcheck').strip()
    
    if not host:
        return False, "Host is required"
    
    if protocol == "Dashboard API":
        try:
            import requests
        except ImportError:
            return False, "requests package not installed"
        
        url = f"http://{host}:{dashboard_port}/api/v5/login"
        
        try:
            response = requests.post(url, json={
                "username": username,
                "password": password
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return True, f"Successfully authenticated to EMQX Dashboard\nVersion: {data.get('version', 'unknown')}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            else:
                return False, f"Dashboard API returned status {response.status_code}"
        except Exception as e:
            return False, f"Dashboard API error: {e}"
    
    elif protocol == "WebSocket":
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            return False, "paho-mqtt package not installed. Run: pip install paho-mqtt"
        
        try:
            client = mqtt.Client(client_id=client_id, transport="websockets")
            if username:
                client.username_pw_set(username, password)
            
            if use_tls:
                import ssl
                client.tls_set(cert_reqs=ssl.CERT_NONE)
                client.tls_insecure_set(True)
            
            result = {"connected": False, "error": None}
            
            def on_connect(client, userdata, flags, rc):
                if rc == 0:
                    result["connected"] = True
                else:
                    result["error"] = f"Connection failed with code {rc}"
            
            client.on_connect = on_connect
            client.connect(host, int(ws_port), 60)
            client.loop_start()
            
            import time
            timeout = 10
            while timeout > 0 and not result["connected"] and not result["error"]:
                time.sleep(0.5)
                timeout -= 0.5
            
            client.loop_stop()
            client.disconnect()
            
            if result["connected"]:
                return True, f"Successfully authenticated to EMQX via WebSocket at {host}:{ws_port}"
            elif result["error"]:
                return False, result["error"]
            else:
                return False, "Connection timeout"
                
        except Exception as e:
            return False, f"WebSocket error: {e}"
    
    else:  # MQTT
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            return False, "paho-mqtt package not installed. Run: pip install paho-mqtt"
        
        try:
            client = mqtt.Client(client_id=client_id)
            if username:
                client.username_pw_set(username, password)
            
            if use_tls:
                import ssl
                client.tls_set(cert_reqs=ssl.CERT_NONE)
                client.tls_insecure_set(True)
            
            result = {"connected": False, "error": None}
            
            def on_connect(client, userdata, flags, rc):
                if rc == 0:
                    result["connected"] = True
                elif rc == 5:
                    result["error"] = "Authentication failed: Invalid credentials"
                else:
                    result["error"] = f"Connection failed with code {rc}"
            
            client.on_connect = on_connect
            client.connect(host, int(mqtt_port), 60)
            client.loop_start()
            
            import time
            timeout = 10
            while timeout > 0 and not result["connected"] and not result["error"]:
                time.sleep(0.5)
                timeout -= 0.5
            
            client.loop_stop()
            client.disconnect()
            
            if result["connected"]:
                return True, f"Successfully authenticated to EMQX at {host}:{mqtt_port}"
            elif result["error"]:
                return False, result["error"]
            else:
                return False, "Connection timeout"
                
        except Exception as e:
            return False, f"MQTT error: {e}"

