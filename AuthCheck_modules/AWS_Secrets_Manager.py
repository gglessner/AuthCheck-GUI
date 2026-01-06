# AWS Secrets Manager Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "AWS Secrets Manager (Security)"

form_fields = [
    {"name": "access_key_id", "type": "text", "label": "Access Key ID"},
    {"name": "secret_access_key", "type": "password", "label": "Secret Access Key"},
    {"name": "session_token", "type": "password", "label": "Session Token (Optional)"},
    {"name": "region", "type": "text", "label": "Region", "default": "us-east-1"},
    {"name": "profile", "type": "text", "label": "Profile Name (Alternative)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Requires secretsmanager:ListSecrets permission. AWS credentials or profile."},
]


def authenticate(form_data):
    """Attempt to authenticate to AWS Secrets Manager."""
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
    except ImportError:
        return False, "boto3 package not installed. Run: pip install boto3"
    
    access_key_id = form_data.get('access_key_id', '').strip()
    secret_access_key = form_data.get('secret_access_key', '').strip()
    session_token = form_data.get('session_token', '').strip()
    region = form_data.get('region', 'us-east-1').strip()
    profile = form_data.get('profile', '').strip()
    
    try:
        if profile:
            session = boto3.Session(profile_name=profile, region_name=region)
        elif access_key_id and secret_access_key:
            session_kwargs = {
                'aws_access_key_id': access_key_id,
                'aws_secret_access_key': secret_access_key,
                'region_name': region
            }
            if session_token:
                session_kwargs['aws_session_token'] = session_token
            session = boto3.Session(**session_kwargs)
        else:
            return False, "Access Key ID and Secret Access Key required (or Profile Name)"
        
        # Create Secrets Manager client
        client = session.client('secretsmanager')
        
        # List secrets
        paginator = client.get_paginator('list_secrets')
        secret_count = 0
        secret_names = []
        
        for page in paginator.paginate(MaxResults=100):
            secrets = page.get('SecretList', [])
            secret_count += len(secrets)
            for secret in secrets[:5]:
                secret_names.append(secret.get('Name', 'unknown'))
        
        return True, f"Successfully authenticated to AWS Secrets Manager\nRegion: {region}\nSecrets: {secret_count}\nSample: {', '.join(secret_names[:3])}{'...' if secret_count > 3 else ''}"
        
    except NoCredentialsError:
        return False, "No AWS credentials found"
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_msg = e.response.get('Error', {}).get('Message', str(e))
        return False, f"AWS error ({error_code}): {error_msg}"
    except Exception as e:
        return False, f"AWS Secrets Manager error: {e}"

