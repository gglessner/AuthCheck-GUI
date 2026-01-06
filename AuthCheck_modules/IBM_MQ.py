# IBM MQ Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "IBM MQ (MQ)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "1414",
     "port_toggle": "use_tls", "tls_port": "1414", "non_tls_port": "1414"},
    {"name": "queue_manager", "type": "text", "label": "Queue Manager"},
    {"name": "channel", "type": "text", "label": "Channel", "default": "SYSTEM.DEF.SVRCONN"},
    {"name": "use_tls", "type": "checkbox", "label": "Enable TLS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "User/Password", "Certificate"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "ssl_cipher", "type": "text", "label": "SSL Cipher Spec", "default": "TLS_RSA_WITH_AES_256_CBC_SHA256"},
    {"name": "key_repository", "type": "file", "label": "Key Repository (.kdb)", "filter": "Key Database (*.kdb);;All Files (*)"},
    {"name": "certificate_label", "type": "text", "label": "Certificate Label"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 1414 (TLS/non-TLS same). mqm / mqm, app / passw0rd. DEV.APP.SVRCONN"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to IBM MQ.
    
    Args:
        form_data (dict): Form field values
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        import pymqi
    except ImportError:
        return False, "pymqi package not installed. Run: pip install pymqi (requires IBM MQ client libraries)"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    queue_manager = form_data.get('queue_manager', '').strip()
    channel = form_data.get('channel', '').strip()
    use_tls = form_data.get('use_tls', False)
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    ssl_cipher = form_data.get('ssl_cipher', '').strip()
    key_repository = form_data.get('key_repository', '').strip()
    certificate_label = form_data.get('certificate_label', '').strip()
    
    if not host:
        return False, "Host is required"
    if not port:
        return False, "Port is required"
    if not queue_manager:
        return False, "Queue Manager is required"
    if not channel:
        return False, "Channel is required"
    
    try:
        conn_info = f"{host}({port})"
        
        cd = pymqi.CD()
        cd.ChannelName = channel.encode('utf-8')
        cd.ConnectionName = conn_info.encode('utf-8')
        cd.ChannelType = pymqi.CMQC.MQCHT_CLNTCONN
        cd.TransportType = pymqi.CMQC.MQXPT_TCP
        
        if use_tls and ssl_cipher:
            cd.SSLCipherSpec = ssl_cipher.encode('utf-8')
        
        sco = pymqi.SCO()
        if use_tls and key_repository:
            # Remove .kdb extension if present
            key_repo = key_repository.replace('.kdb', '')
            sco.KeyRepository = key_repo.encode('utf-8')
            if certificate_label:
                sco.CertificateLabel = certificate_label.encode('utf-8')
        
        qmgr = pymqi.QueueManager(None)
        
        if auth_type == "User/Password" and username:
            qmgr.connect_with_options(
                queue_manager,
                cd=cd,
                sco=sco,
                user=username,
                password=password
            )
        else:
            qmgr.connect_with_options(queue_manager, cd=cd, sco=sco)
        
        # Get queue manager status
        qmgr_name = qmgr.inquire(pymqi.CMQC.MQCA_Q_MGR_NAME).strip()
        qmgr.disconnect()
        
        return True, f"Successfully connected to IBM MQ Queue Manager: {qmgr_name} at {host}:{port}"
        
    except pymqi.MQMIError as e:
        reason_codes = {
            2035: "MQRC_NOT_AUTHORIZED - Authentication failed",
            2059: "MQRC_Q_MGR_NOT_AVAILABLE - Queue manager not available",
            2538: "MQRC_HOST_NOT_AVAILABLE - Host not reachable",
            2539: "MQRC_CONNECTION_BROKEN - Connection broken",
            2540: "MQRC_CONNECTION_ERROR - Connection error",
        }
        reason = reason_codes.get(e.reason, f"MQ Reason Code: {e.reason}")
        return False, f"IBM MQ error: {reason}"
    except Exception as e:
        return False, f"Error: {e}"
