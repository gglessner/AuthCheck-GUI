# MinIO Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "MinIO (Storage)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "9000",
     "port_toggle": "use_ssl", "tls_port": "9000", "non_tls_port": "9000"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "access_key", "type": "text", "label": "Access Key", "default": "minioadmin"},
    {"name": "secret_key", "type": "password", "label": "Secret Key"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API: 9000 (TLS/non-TLS same). minioadmin / minioadmin"},
]


def authenticate(form_data):
    """Attempt to authenticate to MinIO."""
    try:
        from minio import Minio
    except ImportError:
        return False, "minio package not installed. Run: pip install minio"
    
    endpoint = form_data.get('endpoint', '').strip()
    use_ssl = form_data.get('use_ssl', False)
    access_key = form_data.get('access_key', '').strip()
    secret_key = form_data.get('secret_key', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not endpoint:
        return False, "Endpoint is required"
    if not access_key:
        return False, "Access Key is required"
    
    try:
        import urllib3
        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=use_ssl,
            cert_check=verify_ssl
        )
        
        # List buckets to verify access
        buckets = client.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        return True, f"Successfully authenticated to MinIO at {endpoint}\nBuckets: {bucket_names}"
        
    except Exception as e:
        error_msg = str(e)
        if "InvalidAccessKeyId" in error_msg or "SignatureDoesNotMatch" in error_msg:
            return False, "Authentication failed: Invalid credentials"
        return False, f"MinIO error: {e}"

