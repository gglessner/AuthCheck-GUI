# Apache Kafka Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Kafka (MQ)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "9092",
     "port_toggle": "security_protocol", "tls_port": "9093", "non_tls_port": "9092"},
    {"name": "client_library", "type": "combo", "label": "Client Library",
     "options": ["kafka-python", "confluent-kafka"]},
    {"name": "security_protocol", "type": "combo", "label": "Security Protocol", 
     "options": ["PLAINTEXT", "SSL", "SASL_PLAINTEXT", "SASL_SSL"]},
    {"name": "sasl_mechanism", "type": "combo", "label": "SASL Mechanism",
     "options": ["PLAIN", "SCRAM-SHA-256", "SCRAM-SHA-512", "GSSAPI", "OAUTHBEARER"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "ssl_cafile", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "ssl_certfile", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "ssl_keyfile", "type": "file", "label": "Client Key", "filter": "Key Files (*.pem *.key);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "PLAINTEXT: 9092, SSL/SASL_SSL: 9093. admin / admin-secret"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Kafka using kafka-python or confluent-kafka.
    """
    bootstrap_servers = form_data.get('bootstrap_servers', '').strip()
    client_library = form_data.get('client_library', 'kafka-python')
    security_protocol = form_data.get('security_protocol', 'PLAINTEXT')
    sasl_mechanism = form_data.get('sasl_mechanism', 'PLAIN')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    ssl_cafile = form_data.get('ssl_cafile', '').strip() or None
    ssl_certfile = form_data.get('ssl_certfile', '').strip() or None
    ssl_keyfile = form_data.get('ssl_keyfile', '').strip() or None
    
    if not bootstrap_servers:
        return False, "Bootstrap servers is required"
    
    if client_library == "confluent-kafka":
        try:
            from confluent_kafka import Consumer, KafkaException
            from confluent_kafka.admin import AdminClient
        except ImportError:
            return False, "confluent-kafka package not installed. Run: pip install confluent-kafka"
        
        try:
            config = {
                'bootstrap.servers': bootstrap_servers,
                'security.protocol': security_protocol,
                'socket.timeout.ms': 10000,
                'session.timeout.ms': 10000,
            }
            
            # Add SASL config if using SASL
            if 'SASL' in security_protocol:
                config['sasl.mechanism'] = sasl_mechanism
                if sasl_mechanism in ['PLAIN', 'SCRAM-SHA-256', 'SCRAM-SHA-512']:
                    config['sasl.username'] = username
                    config['sasl.password'] = password
            
            # Add SSL config if using SSL
            if 'SSL' in security_protocol:
                if ssl_cafile:
                    config['ssl.ca.location'] = ssl_cafile
                if ssl_certfile:
                    config['ssl.certificate.location'] = ssl_certfile
                if ssl_keyfile:
                    config['ssl.key.location'] = ssl_keyfile
            
            # Use AdminClient to get cluster metadata
            admin = AdminClient(config)
            metadata = admin.list_topics(timeout=10)
            
            broker_count = len(metadata.brokers)
            topic_count = len(metadata.topics)
            cluster_id = metadata.cluster_id or 'unknown'
            
            return True, f"Successfully authenticated to Kafka cluster\nCluster ID: {cluster_id}\nBrokers: {broker_count}, Topics: {topic_count}"
            
        except KafkaException as e:
            return False, f"Kafka error: {e}"
        except Exception as e:
            return False, f"Authentication failed: {e}"
    
    else:  # kafka-python
        try:
            from kafka import KafkaConsumer, KafkaAdminClient
            from kafka.errors import KafkaError
        except ImportError:
            return False, "kafka-python package not installed. Run: pip install kafka-python"
        
        try:
            config = {
                'bootstrap_servers': bootstrap_servers.split(','),
                'security_protocol': security_protocol,
                'request_timeout_ms': 10000,
                'api_version_auto_timeout_ms': 10000,
            }
            
            # Add SASL config if using SASL
            if 'SASL' in security_protocol:
                config['sasl_mechanism'] = sasl_mechanism
                if sasl_mechanism in ['PLAIN', 'SCRAM-SHA-256', 'SCRAM-SHA-512']:
                    config['sasl_plain_username'] = username
                    config['sasl_plain_password'] = password
            
            # Add SSL config if using SSL
            if 'SSL' in security_protocol:
                if ssl_cafile:
                    config['ssl_cafile'] = ssl_cafile
                if ssl_certfile:
                    config['ssl_certfile'] = ssl_certfile
                if ssl_keyfile:
                    config['ssl_keyfile'] = ssl_keyfile
                config['ssl_check_hostname'] = True
            
            # Use AdminClient for better metadata
            try:
                admin = KafkaAdminClient(**config)
                cluster_metadata = admin.describe_cluster()
                broker_count = len(cluster_metadata.get('brokers', []))
                topics = admin.list_topics()
                admin.close()
                
                return True, f"Successfully authenticated to Kafka cluster at {bootstrap_servers}\nBrokers: {broker_count}, Topics: {len(topics)}"
            except:
                # Fallback to consumer
                consumer = KafkaConsumer(**config)
                metadata = consumer.bootstrap_connected()
                topics = consumer.topics()
                consumer.close()
                
                if metadata:
                    return True, f"Successfully authenticated to Kafka cluster at {bootstrap_servers}\nTopics: {len(topics)}"
                else:
                    return False, "Connected but could not verify cluster metadata"
                
        except KafkaError as e:
            return False, f"Kafka error: {e}"
        except Exception as e:
            return False, f"Authentication failed: {e}"
