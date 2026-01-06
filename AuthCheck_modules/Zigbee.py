"""Zigbee/Zigbee2MQTT authentication module."""

module_description = "Zigbee (IoT)"

form_fields = [
    {"name": "host", "type": "text", "label": "Zigbee2MQTT Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "MQTT Port", "default": "1883"},
    {"name": "ws_port", "type": "text", "label": "WebSocket Port", "default": "8080"},
    {"name": "username", "type": "text", "label": "MQTT Username", "default": ""},
    {"name": "password", "type": "password", "label": "MQTT Password", "default": ""},
    {"name": "api_key", "type": "password", "label": "Frontend API Key", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Zigbee2MQTT uses MQTT. Frontend on port 8080. Direct Zigbee needs coordinator."}
]

def authenticate(form_data):
    """Test Zigbee2MQTT authentication."""
    try:
        import paho.mqtt.client as mqtt
        import time
        
        host = form_data.get("host", "localhost")
        port = int(form_data.get("port", 1883))
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        
        result = {"connected": False, "error": None}
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                result["connected"] = True
            else:
                result["error"] = f"Connection failed with code {rc}"
        
        client = mqtt.Client()
        client.on_connect = on_connect
        
        if username:
            client.username_pw_set(username, password)
        
        client.connect(host, port, 60)
        client.loop_start()
        
        # Wait for connection
        timeout = 10
        start = time.time()
        while not result["connected"] and not result["error"]:
            if time.time() - start > timeout:
                result["error"] = "Connection timeout"
                break
            time.sleep(0.1)
        
        client.loop_stop()
        client.disconnect()
        
        if result["connected"]:
            return True, f"Zigbee2MQTT (MQTT) authentication successful at {host}:{port}"
        else:
            return False, result["error"]
            
    except ImportError:
        return False, "paho-mqtt library not installed. Install with: pip install paho-mqtt"
    except Exception as e:
        return False, f"Zigbee error: {str(e)}"

