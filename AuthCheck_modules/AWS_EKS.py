# AWS EKS Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "AWS EKS (Cloud)"

form_fields = [
    {"name": "access_key_id", "type": "text", "label": "Access Key ID"},
    {"name": "secret_access_key", "type": "password", "label": "Secret Access Key"},
    {"name": "region", "type": "text", "label": "Region", "default": "us-east-1"},
    {"name": "cluster_name", "type": "text", "label": "Cluster Name (Optional)"},
    {"name": "profile", "type": "text", "label": "Profile Name (Alternative)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Requires eks:ListClusters or eks:DescribeCluster permission."},
]


def authenticate(form_data):
    """Attempt to authenticate to AWS EKS."""
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
    except ImportError:
        return False, "boto3 package not installed. Run: pip install boto3"
    
    access_key_id = form_data.get('access_key_id', '').strip()
    secret_access_key = form_data.get('secret_access_key', '').strip()
    region = form_data.get('region', 'us-east-1').strip()
    cluster_name = form_data.get('cluster_name', '').strip()
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
        
        eks = session.client('eks')
        
        if cluster_name:
            # Describe specific cluster
            response = eks.describe_cluster(name=cluster_name)
            cluster = response.get('cluster', {})
            status = cluster.get('status', 'unknown')
            version = cluster.get('version', 'unknown')
            endpoint = cluster.get('endpoint', 'unknown')[:50]
            
            return True, f"Successfully authenticated to AWS EKS\nCluster: {cluster_name}\nStatus: {status}\nVersion: {version}"
        else:
            # List clusters
            response = eks.list_clusters()
            clusters = response.get('clusters', [])
            
            return True, f"Successfully authenticated to AWS EKS\nRegion: {region}\nClusters: {len(clusters)}\nNames: {', '.join(clusters[:5])}{'...' if len(clusters) > 5 else ''}"
        
    except NoCredentialsError:
        return False, "No AWS credentials found"
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_msg = e.response.get('Error', {}).get('Message', str(e))
        return False, f"AWS EKS error ({error_code}): {error_msg}"
    except Exception as e:
        return False, f"AWS EKS error: {e}"

