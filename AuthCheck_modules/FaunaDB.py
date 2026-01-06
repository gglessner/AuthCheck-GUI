# FaunaDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "FaunaDB (DB)"


form_fields = [
    {"name": "secret", "type": "password", "label": "Secret Key"},
    {"name": "endpoint", "type": "text", "label": "Endpoint", "default": "https://db.fauna.com"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Secret key from Fauna Dashboard > Security. Serverless document database."},
]


def authenticate(form_data):
    """Attempt to authenticate to FaunaDB."""
    try:
        from faunadb import query as q
        from faunadb.client import FaunaClient
        from faunadb.errors import Unauthorized, BadRequest
    except ImportError:
        return False, "faunadb package not installed. Run: pip install faunadb"
    
    secret = form_data.get('secret', '').strip()
    endpoint = form_data.get('endpoint', 'https://db.fauna.com').strip()
    
    if not secret:
        return False, "Secret Key is required"
    
    try:
        client = FaunaClient(secret=secret, domain=endpoint.replace('https://', '').replace('http://', ''))
        
        # Get databases
        try:
            databases = client.query(q.paginate(q.databases()))
            db_count = len(databases.get('data', []))
        except:
            db_count = 0
        
        # Get collections
        try:
            collections = client.query(q.paginate(q.collections()))
            coll_list = collections.get('data', [])
            coll_count = len(coll_list)
            coll_names = [str(c).split('/')[-1].rstrip('")') for c in coll_list[:5]]
        except:
            coll_count = 0
            coll_names = []
        
        # Get indexes
        try:
            indexes = client.query(q.paginate(q.indexes()))
            index_count = len(indexes.get('data', []))
        except:
            index_count = 0
        
        return True, f"Successfully authenticated to FaunaDB\nEndpoint: {endpoint}\nDatabases: {db_count}\nCollections: {coll_count}\nIndexes: {index_count}"
        
    except Unauthorized:
        return False, "Authentication failed: Invalid secret key"
    except BadRequest as e:
        return False, f"FaunaDB error: {e}"
    except Exception as e:
        return False, f"FaunaDB error: {e}"

