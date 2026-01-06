# Redpanda Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Redpanda (MQ)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "kafka_port", "type": "text", "label": "Kafka API Port", "default": "9092",
     "port_toggle": "use_ssl", "tls_port": "9093", "non_tls_port": "9092"},
    {"name": "admin_port", "type": "text", "label": "Admin API Port", "default": "9644"},
    {"name": "protocol", "type": "combo", "label": "Protocol",
     "options": ["Kafka API", "Admin API"]},
    {"name": "use_ssl", "type": "checkbox", "label": "Enable SSL/TLS"},
    {"name": "sasl_mechanism", "type": "combo", "label": "SASL Mechanism",
     "options": ["PLAIN", "SCRAM-SHA-256", "SCRAM-SHA-512"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Kafka-compatible. Kafka: 9092/9093, Admin: 9644. admin / admin"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Redpanda.
    """
    host = form_data.get('host', '').strip()
    kafka_port = form_data.get('kafka_port', '').strip()
    admin_port = form_data.get('admin_port', '').strip()
    protocol = form_data.get('protocol', 'Kafka API')
    use_ssl = form_data.get('use_ssl', False)
    sasl_mechanism = form_data.get('sasl_mechanism', 'PLAIN')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    
    if protocol == "Admin API":
        try:
            import requests
        except ImportError:
            return False, "requests package not installed"
        
        scheme = "https" if use_ssl else "http"
        url = f"{scheme}://{host}:{admin_port}/v1/cluster/health_overview"
        
        try:
            auth = (username, password) if username else None
            response = requests.get(url, auth=auth, verify=verify_ssl, timeout=10)
            
            if response.status_code == 200:
                return True, f"Successfully connected to Redpanda Admin API at {host}:{admin_port}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            else:
                return False, f"Admin API returned status {response.status_code}"
        except Exception as e:
            return False, f"Admin API error: {e}"
    else:
        try:
            from kafka import KafkaConsumer
            from kafka.errors import KafkaError
        except ImportError:
            return False, "kafka-python package not installed. Run: pip install kafka-python"
        
        try:
            config = {
                'bootstrap_servers': f"{host}:{kafka_port}",
                'client_id': 'authcheck-redpanda',
                'request_timeout_ms': 10000,
                'api_version_auto_timeout_ms': 10000,
            }
            
            if username:
                config['security_protocol'] = 'SASL_SSL' if use_ssl else 'SASL_PLAINTEXT'
                config['sasl_mechanism'] = sasl_mechanism
                config['sasl_plain_username'] = username
                config['sasl_plain_password'] = password
            elif use_ssl:
                config['security_protocol'] = 'SSL'
            
            if use_ssl and not verify_ssl:
                config['ssl_check_hostname'] = False
                import ssl
                config['ssl_context'] = ssl._create_unverified_context()
            
            consumer = KafkaConsumer(**config)
            topics = consumer.topics()
            consumer.close()
            
            return True, f"Successfully authenticated to Redpanda at {host}:{kafka_port}\nTopics: {len(topics)}"
            
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg or "sasl" in error_msg:
                return False, f"Authentication failed: {e}"
            return False, f"Kafka API error: {e}"

