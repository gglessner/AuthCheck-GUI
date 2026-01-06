# AWS EC2 Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "AWS EC2 (Cloud)"

form_fields = [
    {"name": "access_key_id", "type": "text", "label": "Access Key ID"},
    {"name": "secret_access_key", "type": "password", "label": "Secret Access Key"},
    {"name": "region", "type": "text", "label": "Region", "default": "us-east-1"},
    {"name": "profile", "type": "text", "label": "Profile Name (Alternative)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Requires ec2:DescribeInstances permission."},
]


def authenticate(form_data):
    """Attempt to authenticate to AWS EC2."""
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
    except ImportError:
        return False, "boto3 package not installed. Run: pip install boto3"
    
    access_key_id = form_data.get('access_key_id', '').strip()
    secret_access_key = form_data.get('secret_access_key', '').strip()
    region = form_data.get('region', 'us-east-1').strip()
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
        
        ec2 = session.client('ec2')
        
        # Describe instances
        response = ec2.describe_instances()
        reservations = response.get('Reservations', [])
        
        running_count = 0
        stopped_count = 0
        total_count = 0
        
        for reservation in reservations:
            for instance in reservation.get('Instances', []):
                total_count += 1
                state = instance.get('State', {}).get('Name', '')
                if state == 'running':
                    running_count += 1
                elif state == 'stopped':
                    stopped_count += 1
        
        # Get VPC count
        vpcs_resp = ec2.describe_vpcs()
        vpc_count = len(vpcs_resp.get('Vpcs', []))
        
        # Get security group count
        sgs_resp = ec2.describe_security_groups()
        sg_count = len(sgs_resp.get('SecurityGroups', []))
        
        return True, f"Successfully authenticated to AWS EC2\nRegion: {region}\nInstances: {total_count} (Running: {running_count}, Stopped: {stopped_count})\nVPCs: {vpc_count}\nSecurity Groups: {sg_count}"
        
    except NoCredentialsError:
        return False, "No AWS credentials found"
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_msg = e.response.get('Error', {}).get('Message', str(e))
        return False, f"AWS EC2 error ({error_code}): {error_msg}"
    except Exception as e:
        return False, f"AWS EC2 error: {e}"

