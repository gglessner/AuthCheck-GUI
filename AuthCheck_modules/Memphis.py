# Memphis Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Memphis (MQ)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "6666"},
    {"name": "http_port", "type": "text", "label": "HTTP Port", "default": "9000"},
    {"name": "protocol", "type": "combo", "label": "Protocol",
     "options": ["Memphis SDK", "REST API"]},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password/Token"},
    {"name": "account_id", "type": "text", "label": "Account ID", "default": "1"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "SDK: 6666, HTTP: 9000. root / memphis"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Memphis.
    """
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    http_port = form_data.get('http_port', '').strip()
    protocol = form_data.get('protocol', 'Memphis SDK')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    account_id = form_data.get('account_id', '1').strip()
    
    if not host:
        return False, "Host is required"
    
    if protocol == "REST API":
        try:
            import requests
        except ImportError:
            return False, "requests package not installed"
        
        url = f"http://{host}:{http_port}/api/auth/authenticate"
        
        try:
            response = requests.post(url, json={
                "username": username,
                "password": password
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return True, f"Successfully authenticated to Memphis at {host}:{http_port}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            else:
                return False, f"REST API returned status {response.status_code}"
        except Exception as e:
            return False, f"REST API error: {e}"
    
    else:  # Memphis SDK
        try:
            from memphis import Memphis
            import asyncio
        except ImportError:
            return False, "memphis-py package not installed. Run: pip install memphis-py"
        
        async def connect_memphis():
            memphis = Memphis()
            await memphis.connect(
                host=host,
                username=username,
                password=password,
                account_id=int(account_id),
                port=int(port),
                reconnect=False,
                max_reconnect=1,
                connection_timeout=10
            )
            await memphis.close()
            return True
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(connect_memphis())
                return True, f"Successfully authenticated to Memphis at {host}:{port}"
            finally:
                loop.close()
                
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg or "credentials" in error_msg:
                return False, f"Authentication failed: {e}"
            return False, f"Memphis error: {e}"

