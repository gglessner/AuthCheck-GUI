# AWS DynamoDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "AWS DynamoDB (Cloud)"

form_fields = [
    {"name": "access_key_id", "type": "text", "label": "Access Key ID"},
    {"name": "secret_access_key", "type": "password", "label": "Secret Access Key"},
    {"name": "region", "type": "text", "label": "Region", "default": "us-east-1"},
    {"name": "table_name", "type": "text", "label": "Test Table (Optional)"},
    {"name": "profile", "type": "text", "label": "Profile Name (Alternative)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Requires dynamodb:ListTables or dynamodb:DescribeTable permission."},
]


def authenticate(form_data):
    """Attempt to authenticate to AWS DynamoDB."""
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
    except ImportError:
        return False, "boto3 package not installed. Run: pip install boto3"
    
    access_key_id = form_data.get('access_key_id', '').strip()
    secret_access_key = form_data.get('secret_access_key', '').strip()
    region = form_data.get('region', 'us-east-1').strip()
    table_name = form_data.get('table_name', '').strip()
    profile = form_data.get('profile', '').strip()
    
    try:
        if profile:
            session = boto3.Session(profile_name=profile, region_name=region)
        elif access_key_id and secret_access_key:
            session = boto3.Session(
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region
            )
        else:
            return False, "Access Key ID and Secret Access Key required (or Profile Name)"
        
        dynamodb = session.client('dynamodb')
        
        if table_name:
            # Describe specific table
            response = dynamodb.describe_table(TableName=table_name)
            table = response.get('Table', {})
            status = table.get('TableStatus', 'unknown')
            item_count = table.get('ItemCount', 0)
            return True, f"Successfully authenticated to AWS DynamoDB\nTable: {table_name}\nStatus: {status}\nItems: {item_count}"
        else:
            # List tables
            response = dynamodb.list_tables()
            tables = response.get('TableNames', [])
            
            return True, f"Successfully authenticated to AWS DynamoDB\nRegion: {region}\nTables: {len(tables)}\nSample: {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}"
        
    except NoCredentialsError:
        return False, "No AWS credentials found"
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_msg = e.response.get('Error', {}).get('Message', str(e))
        return False, f"AWS DynamoDB error ({error_code}): {error_msg}"
    except Exception as e:
        return False, f"AWS DynamoDB error: {e}"

