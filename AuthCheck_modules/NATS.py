# NATS Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "NATS (MQ)"

form_fields = [
    {"name": "servers", "type": "text", "label": "Servers", "default": "nats://localhost:4222"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "Username/Password", "Token", "NKey", "JWT/Creds"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "token", "type": "password", "label": "Token"},
    {"name": "nkey_seed", "type": "password", "label": "NKey Seed"},
    {"name": "creds_file", "type": "file", "label": "Credentials File", "filter": "Credentials (*.creds);;All Files (*)"},
    {"name": "tls_ca", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: no auth. Common: admin / admin, nats / nats"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to NATS.
    """
    try:
        import nats
        import asyncio
    except ImportError:
        return False, "nats-py package not installed. Run: pip install nats-py"
    
    servers = form_data.get('servers', '').strip()
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    token = form_data.get('token', '').strip()
    nkey_seed = form_data.get('nkey_seed', '').strip()
    creds_file = form_data.get('creds_file', '').strip()
    tls_ca = form_data.get('tls_ca', '').strip()
    
    if not servers:
        return False, "Servers is required"
    
    async def connect_nats():
        connect_kwargs = {
            'servers': servers.split(','),
            'connect_timeout': 10,
            'max_reconnect_attempts': 1,
        }
        
        if auth_type == "Username/Password" and username:
            connect_kwargs['user'] = username
            connect_kwargs['password'] = password
        elif auth_type == "Token" and token:
            connect_kwargs['token'] = token
        elif auth_type == "NKey" and nkey_seed:
            connect_kwargs['nkeys_seed'] = nkey_seed
        elif auth_type == "JWT/Creds" and creds_file:
            connect_kwargs['user_credentials'] = creds_file
        
        if tls_ca:
            import ssl
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.load_verify_locations(tls_ca)
            connect_kwargs['tls'] = ssl_ctx
        
        nc = await nats.connect(**connect_kwargs)
        
        server_info = {
            'server_id': nc.connected_server_id,
            'server_name': nc._server_info.get('server_name', 'unknown'),
            'version': nc._server_info.get('version', 'unknown'),
        }
        
        await nc.close()
        return server_info
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            info = loop.run_until_complete(connect_nats())
            return True, f"Successfully connected to NATS {info['version']}\nServer: {info['server_name']}"
        finally:
            loop.close()
            
    except Exception as e:
        error_msg = str(e)
        if "Authorization" in error_msg or "authentication" in error_msg.lower():
            return False, f"Authentication failed: {e}"
        return False, f"NATS error: {e}"

