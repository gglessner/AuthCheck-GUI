# Apache RocketMQ Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache RocketMQ (MQ)"

form_fields = [
    {"name": "host", "type": "text", "label": "NameServer Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "NameServer Port", "default": "9876"},
    {"name": "broker_port", "type": "text", "label": "Broker Port", "default": "10911"},
    {"name": "use_acl", "type": "checkbox", "label": "Enable ACL"},
    {"name": "access_key", "type": "text", "label": "Access Key"},
    {"name": "secret_key", "type": "password", "label": "Secret Key"},
    {"name": "group", "type": "text", "label": "Consumer Group", "default": "authcheck_group"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "NameServer: 9876, Broker: 10911. Default: no ACL"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache RocketMQ.
    """
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    broker_port = form_data.get('broker_port', '').strip()
    use_acl = form_data.get('use_acl', False)
    access_key = form_data.get('access_key', '').strip()
    secret_key = form_data.get('secret_key', '')
    group = form_data.get('group', 'authcheck_group').strip()
    
    if not host:
        return False, "NameServer host is required"
    if not port:
        return False, "NameServer port is required"
    
    try:
        from rocketmq.client import PushConsumer, ConsumeStatus
    except ImportError:
        return False, "rocketmq-client-python package not installed. Run: pip install rocketmq-client-python"
    
    try:
        consumer = PushConsumer(group)
        consumer.set_name_server_address(f"{host}:{port}")
        
        if use_acl and access_key and secret_key:
            consumer.set_session_credentials(access_key, secret_key, '')
        
        def callback(msg):
            return ConsumeStatus.CONSUME_SUCCESS
        
        consumer.subscribe("AUTHCHECK_TEST", callback)
        consumer.start()
        consumer.shutdown()
        
        return True, f"Successfully connected to RocketMQ at {host}:{port}"
        
    except Exception as e:
        error_msg = str(e).lower()
        if "acl" in error_msg or "authentication" in error_msg or "permission" in error_msg:
            return False, f"Authentication failed: {e}"
        return False, f"RocketMQ error: {e}"

