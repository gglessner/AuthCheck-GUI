# AWS IAM Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "AWS IAM (Cloud)"

form_fields = [
    {"name": "access_key_id", "type": "text", "label": "Access Key ID"},
    {"name": "secret_access_key", "type": "password", "label": "Secret Access Key"},
    {"name": "session_token", "type": "password", "label": "Session Token (Optional)"},
    {"name": "region", "type": "text", "label": "Region", "default": "us-east-1"},
    {"name": "profile", "type": "text", "label": "Profile Name (Alternative)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Access Key: AKIA... or ASIA... (temp). From IAM > Users > Security Credentials."},
]


def authenticate(form_data):
    """Attempt to authenticate to AWS IAM."""
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
        
        # Get caller identity
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        
        account_id = identity.get('Account', 'unknown')
        arn = identity.get('Arn', 'unknown')
        user_id = identity.get('UserId', 'unknown')
        
        # Determine identity type
        if ':user/' in arn:
            identity_type = 'IAM User'
            identity_name = arn.split(':user/')[-1]
        elif ':role/' in arn:
            identity_type = 'IAM Role'
            identity_name = arn.split(':role/')[-1]
        elif ':assumed-role/' in arn:
            identity_type = 'Assumed Role'
            identity_name = arn.split(':assumed-role/')[-1]
        else:
            identity_type = 'Unknown'
            identity_name = arn
        
        return True, f"Successfully authenticated to AWS\nAccount: {account_id}\n{identity_type}: {identity_name}\nUser ID: {user_id}\nRegion: {region}"
        
    except NoCredentialsError:
        return False, "No AWS credentials found"
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_msg = e.response.get('Error', {}).get('Message', str(e))
        return False, f"AWS error ({error_code}): {error_msg}"
    except Exception as e:
        return False, f"AWS error: {e}"

