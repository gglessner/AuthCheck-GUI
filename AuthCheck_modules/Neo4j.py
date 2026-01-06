# Neo4j Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Neo4j (DB)"

form_fields = [
    {"name": "uri", "type": "text", "label": "URI", "default": "bolt://localhost:7687"},
    {"name": "username", "type": "text", "label": "Username", "default": "neo4j"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "database", "type": "text", "label": "Database", "default": "neo4j"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "neo4j / neo4j (must change on first login). Bolt port 7687, HTTP 7474."},
]


def authenticate(form_data):
    """Attempt to authenticate to Neo4j."""
    try:
        from neo4j import GraphDatabase
    except ImportError:
        return False, "neo4j package not installed. Run: pip install neo4j"
    
    uri = form_data.get('uri', 'bolt://localhost:7687').strip()
    username = form_data.get('username', 'neo4j').strip()
    password = form_data.get('password', '')
    database = form_data.get('database', 'neo4j').strip()
    
    if not uri:
        return False, "URI is required"
    if not username:
        return False, "Username is required"
    
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        with driver.session(database=database) as session:
            # Get version
            result = session.run("CALL dbms.components() YIELD name, versions RETURN name, versions")
            record = result.single()
            name = record['name'] if record else 'Neo4j'
            version = record['versions'][0] if record and record['versions'] else 'unknown'
            
            # Get node count
            result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()['count']
            
            # Get relationship count
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = result.single()['count']
            
            # Get database list
            result = session.run("SHOW DATABASES")
            databases = [record['name'] for record in result]
        
        driver.close()
        
        return True, f"Successfully authenticated to {name} {version}\nDatabase: {database}\nNodes: {node_count}\nRelationships: {rel_count}\nDatabases: {len(databases)}"
        
    except Exception as e:
        error_msg = str(e)
        if 'authentication' in error_msg.lower() or 'unauthorized' in error_msg.lower():
            return False, "Authentication failed: Invalid credentials"
        return False, f"Neo4j error: {e}"

