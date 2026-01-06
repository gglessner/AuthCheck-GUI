# AWS S3 Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "AWS S3 (Cloud)"

form_fields = [
    {"name": "access_key_id", "type": "text", "label": "Access Key ID"},
    {"name": "secret_access_key", "type": "password", "label": "Secret Access Key"},
    {"name": "session_token", "type": "password", "label": "Session Token (Optional)"},
    {"name": "region", "type": "text", "label": "Region", "default": "us-east-1"},
    {"name": "bucket", "type": "text", "label": "Test Bucket (Optional)"},
    {"name": "profile", "type": "text", "label": "Profile Name (Alternative)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Access Key: AKIA... Requires s3:ListBuckets or s3:ListBucket permission."},
]


def authenticate(form_data):
    """Attempt to authenticate to AWS S3."""
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
    except ImportError:
        return False, "boto3 package not installed. Run: pip install boto3"
    
    access_key_id = form_data.get('access_key_id', '').strip()
    secret_access_key = form_data.get('secret_access_key', '').strip()
    session_token = form_data.get('session_token', '').strip()
    region = form_data.get('region', 'us-east-1').strip()
    bucket = form_data.get('bucket', '').strip()
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
        
        s3 = session.client('s3')
        
        if bucket:
            # Test specific bucket access
            response = s3.head_bucket(Bucket=bucket)
            return True, f"Successfully authenticated to AWS S3\nBucket '{bucket}' is accessible\nRegion: {region}"
        else:
            # List buckets
            response = s3.list_buckets()
            buckets = response.get('Buckets', [])
            bucket_names = [b['Name'] for b in buckets[:5]]
            
            return True, f"Successfully authenticated to AWS S3\nRegion: {region}\nBuckets: {len(buckets)}\nSample: {', '.join(bucket_names)}{'...' if len(buckets) > 5 else ''}"
        
    except NoCredentialsError:
        return False, "No AWS credentials found"
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_msg = e.response.get('Error', {}).get('Message', str(e))
        return False, f"AWS S3 error ({error_code}): {error_msg}"
    except Exception as e:
        return False, f"AWS S3 error: {e}"

