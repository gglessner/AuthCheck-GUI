# Apache Hadoop HDFS Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Hadoop HDFS (BigData)"

form_fields = [
    {"name": "namenode_host", "type": "text", "label": "NameNode Host", "default": "localhost"},
    {"name": "namenode_port", "type": "text", "label": "NameNode Port", "default": "9870",
     "port_toggle": "use_https", "tls_port": "9871", "non_tls_port": "9870"},
    {"name": "webhdfs_port", "type": "text", "label": "WebHDFS Port", "default": "9870",
     "port_toggle": "use_https", "tls_port": "9871", "non_tls_port": "9870"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["Simple", "Kerberos"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "kerberos_principal", "type": "text", "label": "Kerberos Principal"},
    {"name": "keytab_file", "type": "file", "label": "Keytab File", "filter": "Keytab Files (*.keytab);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 9871, Non-TLS: 9870. Simple: hdfs. Kerberos: hdfs/hostname@REALM"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Hadoop HDFS via WebHDFS.
    """
    namenode_host = form_data.get('namenode_host', '').strip()
    webhdfs_port = form_data.get('webhdfs_port', '').strip()
    use_https = form_data.get('use_https', False)
    auth_type = form_data.get('auth_type', 'Simple')
    username = form_data.get('username', '').strip()
    
    if not namenode_host:
        return False, "NameNode Host is required"
    if not webhdfs_port:
        return False, "WebHDFS Port is required"
    
    # Try using hdfs library first
    try:
        from hdfs import InsecureClient, Client
        from hdfs.ext.kerberos import KerberosClient
        
        scheme = "https" if use_https else "http"
        url = f"{scheme}://{namenode_host}:{webhdfs_port}"
        
        if auth_type == "Kerberos":
            client = KerberosClient(url)
        else:
            client = InsecureClient(url, user=username if username else None)
        
        # Try to list root directory
        root_contents = client.list('/')
        
        return True, f"Successfully authenticated to HDFS at {url}\nRoot directory contains {len(root_contents)} items"
        
    except ImportError:
        pass
    except Exception as e:
        if "401" in str(e) or "403" in str(e) or "Unauthorized" in str(e):
            return False, f"Authentication failed: {e}"
        # Continue to fallback
    
    # Fallback to direct HTTP request
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        scheme = "https" if use_https else "http"
        url = f"{scheme}://{namenode_host}:{webhdfs_port}/webhdfs/v1/?op=LISTSTATUS"
        
        if username:
            url += f"&user.name={username}"
        
        response = requests.get(url, timeout=10, verify=False)
        
        if response.status_code == 200:
            return True, f"Successfully connected to HDFS WebHDFS at {namenode_host}:{webhdfs_port}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        elif response.status_code == 403:
            return False, "Authentication failed: Forbidden"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    except Exception as e:
        return False, f"Error: {e}"

