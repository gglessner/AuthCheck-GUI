# Solace PubSub+ Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Solace PubSub+ (MQ)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "SMF Port", "default": "55443",
     "port_toggle": "use_tls", "tls_port": "55443", "non_tls_port": "55555"},
    {"name": "vpn", "type": "text", "label": "Message VPN", "default": "default"},
    {"name": "use_tls", "type": "checkbox", "label": "Enable TLS", "default": True},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL Certificate"},
    {"name": "auth_type", "type": "combo", "label": "Authentication Type",
     "options": ["Basic", "Client Certificate"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "trust_store", "type": "file", "label": "Trust Store (optional)", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "client_cert", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
    {"name": "client_key", "type": "file", "label": "Client Key", "filter": "Key Files (*.pem *.key);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 55443, Non-TLS: 55555. admin / admin, default / default"},
]


# Check if solace SDK is available at module load time
SOLACE_SDK_AVAILABLE = False
SOLACE_SDK_ERROR = None

try:
    from solace.messaging.messaging_service import MessagingService
    from solace.messaging.config.retry_strategy import RetryStrategy
    SOLACE_SDK_AVAILABLE = True
except ImportError as e:
    SOLACE_SDK_ERROR = str(e)
except Exception as e:
    SOLACE_SDK_ERROR = str(e)


def authenticate(form_data):
    """
    Attempt to authenticate to Solace PubSub+.
    
    Args:
        form_data (dict): Form field values
        
    Returns:
        tuple: (success: bool, message: str)
    """
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    vpn = form_data.get('vpn', '').strip()
    use_tls = form_data.get('use_tls', False)
    verify_ssl = form_data.get('verify_ssl', False)
    auth_type = form_data.get('auth_type', 'Basic')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    trust_store = form_data.get('trust_store', '').strip()
    client_cert = form_data.get('client_cert', '').strip()
    client_key = form_data.get('client_key', '').strip()
    
    if not host:
        return False, "Host is required"
    if not port:
        return False, "Port is required"
    if not vpn:
        return False, "Message VPN is required"
    
    # Use Solace SDK if available
    if SOLACE_SDK_AVAILABLE:
        try:
            protocol = "tcps" if use_tls else "tcp"
            broker_props = {
                "solace.messaging.transport.host": f"{protocol}://{host}:{port}",
                "solace.messaging.service.vpn-name": vpn,
            }
            
            if auth_type == "Basic":
                if not username:
                    return False, "Username is required for Basic authentication"
                broker_props["solace.messaging.authentication.scheme.basic.username"] = username
                broker_props["solace.messaging.authentication.scheme.basic.password"] = password
            elif auth_type == "Client Certificate":
                broker_props["solace.messaging.authentication.scheme"] = "AUTHENTICATION_SCHEME_CLIENT_CERTIFICATE"
                if client_cert:
                    broker_props["solace.messaging.authentication.client-cert.file"] = client_cert
                if client_key:
                    broker_props["solace.messaging.authentication.client-cert.private-key-file"] = client_key
            
            # TLS settings
            if use_tls:
                if not verify_ssl:
                    # Disable server certificate validation
                    broker_props["solace.messaging.tls.cert-validated"] = False
                    broker_props["solace.messaging.tls.cert-validated-date"] = False
                else:
                    broker_props["solace.messaging.tls.cert-validated"] = True
                    if trust_store:
                        broker_props["solace.messaging.tls.trust-store-path"] = trust_store
            
            # Build and connect
            messaging_service = MessagingService.builder()\
                .from_properties(broker_props)\
                .with_reconnection_retry_strategy(RetryStrategy.parametrized_retry(0, 1))\
                .build()
            
            messaging_service.connect()
            
            if messaging_service.is_connected:
                messaging_service.disconnect()
                return True, f"Successfully authenticated to Solace broker at {host}:{port} (VPN: {vpn}, User: {username})"
            else:
                return False, "Connection failed - not authenticated"
                
        except Exception as e:
            error_msg = str(e)
            # Parse common Solace errors
            if "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
                return False, f"Authentication failed: Invalid credentials"
            elif "timeout" in error_msg.lower():
                return False, f"Connection timeout to {host}:{port}"
            elif "refused" in error_msg.lower():
                return False, f"Connection refused by {host}:{port}"
            elif "certificate" in error_msg.lower() or "ssl" in error_msg.lower() or "tls" in error_msg.lower():
                return False, f"TLS/SSL error: {error_msg}"
            else:
                return False, f"Solace error: {error_msg}"
    
    # SDK not available - try SEMP REST API as alternative
    try:
        import requests
        
        # Try SEMP management API (typically on port 8080 or 943)
        semp_ports = ["8080", "943", "80"]
        
        for semp_port in semp_ports:
            try:
                scheme = "https" if use_tls else "http"
                semp_url = f"{scheme}://{host}:{semp_port}/SEMP/v2/config/msgVpns/{vpn}"
                
                response = requests.get(
                    semp_url,
                    auth=(username, password),
                    timeout=10,
                    verify=verify_ssl if use_tls else True
                )
                
                if response.status_code == 200:
                    return True, f"Successfully authenticated via SEMP API at {host}:{semp_port} (VPN: {vpn})"
                elif response.status_code == 401:
                    return False, "Authentication failed: Invalid credentials"
                elif response.status_code == 403:
                    return False, "Authentication failed: Access forbidden"
                    
            except requests.exceptions.ConnectionError:
                continue
            except requests.exceptions.Timeout:
                continue
        
        return False, f"solace-pubsubplus SDK not installed ({SOLACE_SDK_ERROR}). SEMP API also not reachable. Install with: pip install solace-pubsubplus"
        
    except ImportError:
        return False, f"solace-pubsubplus SDK not installed ({SOLACE_SDK_ERROR}). Install with: pip install solace-pubsubplus"
    except Exception as e:
        return False, f"Error: {e}. solace-pubsubplus SDK error: {SOLACE_SDK_ERROR}"
