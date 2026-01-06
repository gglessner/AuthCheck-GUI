# SNMP Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "SNMP (Protocol)"

form_fields = [
    {"name": "host", "type": "text", "label": "Target Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "161"},
    {"name": "version", "type": "combo", "label": "SNMP Version", "options": ["v1", "v2c", "v3"], "default": "v2c"},
    {"name": "community", "type": "text", "label": "Community String (v1/v2c)", "default": "public"},
    {"name": "username", "type": "text", "label": "Username (v3)"},
    {"name": "auth_protocol", "type": "combo", "label": "Auth Protocol (v3)", "options": ["None", "MD5", "SHA", "SHA-224", "SHA-256", "SHA-384", "SHA-512"], "default": "SHA"},
    {"name": "auth_password", "type": "password", "label": "Auth Password (v3)"},
    {"name": "priv_protocol", "type": "combo", "label": "Privacy Protocol (v3)", "options": ["None", "DES", "3DES", "AES-128", "AES-192", "AES-256"], "default": "AES-128"},
    {"name": "priv_password", "type": "password", "label": "Privacy Password (v3)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Common communities: public, private, community. v3 requires username + auth."},
]


def authenticate(form_data):
    """Attempt to authenticate to SNMP."""
    try:
        from pysnmp.hlapi import (
            SnmpEngine, CommunityData, UsmUserData, UdpTransportTarget,
            ContextData, ObjectType, ObjectIdentity, getCmd,
            usmHMACMD5AuthProtocol, usmHMACSHAAuthProtocol,
            usmHMAC128SHA224AuthProtocol, usmHMAC192SHA256AuthProtocol,
            usmHMAC256SHA384AuthProtocol, usmHMAC384SHA512AuthProtocol,
            usmDESPrivProtocol, usm3DESEDEPrivProtocol,
            usmAesCfb128Protocol, usmAesCfb192Protocol, usmAesCfb256Protocol,
            usmNoAuthProtocol, usmNoPrivProtocol
        )
    except ImportError:
        return False, "pysnmp package not installed. Run: pip install pysnmp"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '161').strip()
    version = form_data.get('version', 'v2c')
    community = form_data.get('community', 'public').strip()
    username = form_data.get('username', '').strip()
    auth_protocol = form_data.get('auth_protocol', 'None')
    auth_password = form_data.get('auth_password', '')
    priv_protocol = form_data.get('priv_protocol', 'None')
    priv_password = form_data.get('priv_password', '')
    
    if not host:
        return False, "Target Host is required"
    
    try:
        # Map auth protocols
        auth_proto_map = {
            'None': usmNoAuthProtocol,
            'MD5': usmHMACMD5AuthProtocol,
            'SHA': usmHMACSHAAuthProtocol,
            'SHA-224': usmHMAC128SHA224AuthProtocol,
            'SHA-256': usmHMAC192SHA256AuthProtocol,
            'SHA-384': usmHMAC256SHA384AuthProtocol,
            'SHA-512': usmHMAC384SHA512AuthProtocol,
        }
        
        # Map privacy protocols
        priv_proto_map = {
            'None': usmNoPrivProtocol,
            'DES': usmDESPrivProtocol,
            '3DES': usm3DESEDEPrivProtocol,
            'AES-128': usmAesCfb128Protocol,
            'AES-192': usmAesCfb192Protocol,
            'AES-256': usmAesCfb256Protocol,
        }
        
        if version in ['v1', 'v2c']:
            # SNMPv1/v2c uses community string
            mpModel = 0 if version == 'v1' else 1
            auth_data = CommunityData(community, mpModel=mpModel)
        else:
            # SNMPv3
            if not username:
                return False, "Username required for SNMPv3"
            
            auth_proto = auth_proto_map.get(auth_protocol, usmNoAuthProtocol)
            priv_proto = priv_proto_map.get(priv_protocol, usmNoPrivProtocol)
            
            if auth_protocol != 'None' and not auth_password:
                return False, "Auth password required when auth protocol is set"
            
            if priv_protocol != 'None' and not priv_password:
                return False, "Privacy password required when privacy protocol is set"
            
            auth_data = UsmUserData(
                username,
                authKey=auth_password if auth_protocol != 'None' else None,
                privKey=priv_password if priv_protocol != 'None' else None,
                authProtocol=auth_proto,
                privProtocol=priv_proto
            )
        
        # Try to get sysDescr.0
        iterator = getCmd(
            SnmpEngine(),
            auth_data,
            UdpTransportTarget((host, int(port)), timeout=5, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)),
            ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0)),
            ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysUpTime', 0))
        )
        
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
        
        if errorIndication:
            return False, f"SNMP error: {errorIndication}"
        elif errorStatus:
            return False, f"SNMP error: {errorStatus.prettyPrint()} at {errorIndex}"
        else:
            results = {}
            for varBind in varBinds:
                name = str(varBind[0]).split('::')[-1]
                value = str(varBind[1])
                results[name] = value
            
            sys_descr = results.get('sysDescr', 'N/A')[:100]
            sys_name = results.get('sysName', 'N/A')
            uptime = results.get('sysUpTime', 'N/A')
            
            return True, f"Successfully authenticated to SNMP ({version})\nHost: {host}:{port}\nSystem: {sys_name}\nDescription: {sys_descr}\nUptime: {uptime}"
            
    except Exception as e:
        return False, f"SNMP error: {e}"

