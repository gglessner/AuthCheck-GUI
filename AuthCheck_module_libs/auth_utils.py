# AuthCheck shared utilities
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import ssl
import socket


def create_ssl_context(use_tls=True, verify_cert=True, cert_file=None, key_file=None, ca_file=None):
    """
    Create an SSL context for secure connections.
    
    Args:
        use_tls (bool): Whether to use TLS
        verify_cert (bool): Whether to verify server certificate
        cert_file (str): Path to client certificate file
        key_file (str): Path to client key file
        ca_file (str): Path to CA certificate file
        
    Returns:
        ssl.SSLContext or None if TLS is disabled
    """
    if not use_tls:
        return None
    
    context = ssl.create_default_context()
    
    if not verify_cert:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    
    if ca_file:
        context.load_verify_locations(ca_file)
    
    if cert_file:
        context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    
    return context


def test_tcp_connection(host, port, timeout=10, ssl_context=None):
    """
    Test a basic TCP connection to a host:port.
    
    Args:
        host (str): Hostname or IP address
        port (int): Port number
        timeout (int): Connection timeout in seconds
        ssl_context (ssl.SSLContext): Optional SSL context for TLS connections
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        if ssl_context:
            sock = ssl_context.wrap_socket(sock, server_hostname=host)
        
        sock.connect((host, int(port)))
        sock.close()
        return True, f"Successfully connected to {host}:{port}"
    except socket.timeout:
        return False, f"Connection timed out after {timeout} seconds"
    except ConnectionRefusedError:
        return False, f"Connection refused by {host}:{port}"
    except ssl.SSLError as e:
        return False, f"SSL error: {e}"
    except Exception as e:
        return False, f"Connection error: {e}"


def validate_required_fields(form_data, required_fields):
    """
    Validate that required fields are present and non-empty.
    
    Args:
        form_data (dict): Form data dictionary
        required_fields (list): List of required field names
        
    Returns:
        tuple: (valid: bool, missing_fields: list)
    """
    missing = []
    for field in required_fields:
        value = form_data.get(field, '')
        if isinstance(value, str) and not value.strip():
            missing.append(field)
        elif value is None:
            missing.append(field)
    
    return len(missing) == 0, missing

