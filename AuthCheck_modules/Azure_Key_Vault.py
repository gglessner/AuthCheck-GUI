# Azure Key Vault Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Azure Key Vault (Security)"

form_fields = [
    {"name": "vault_url", "type": "text", "label": "Vault URL"},
    {"name": "tenant_id", "type": "text", "label": "Tenant ID"},
    {"name": "client_id", "type": "text", "label": "Client ID (App ID)"},
    {"name": "client_secret", "type": "password", "label": "Client Secret"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Vault URL: https://vault-name.vault.azure.net. App registration needs Key Vault access policy."},
]


def authenticate(form_data):
    """Attempt to authenticate to Azure Key Vault."""
    try:
        from azure.identity import ClientSecretCredential
        from azure.keyvault.secrets import SecretClient
    except ImportError:
        return False, "azure-identity and azure-keyvault-secrets packages not installed. Run: pip install azure-identity azure-keyvault-secrets"
    
    vault_url = form_data.get('vault_url', '').strip()
    tenant_id = form_data.get('tenant_id', '').strip()
    client_id = form_data.get('client_id', '').strip()
    client_secret = form_data.get('client_secret', '')
    
    if not vault_url:
        return False, "Vault URL is required"
    if not tenant_id:
        return False, "Tenant ID is required"
    if not client_id:
        return False, "Client ID is required"
    if not client_secret:
        return False, "Client Secret is required"
    
    if not vault_url.startswith('http'):
        vault_url = f"https://{vault_url}"
    if not vault_url.endswith('.vault.azure.net'):
        vault_url = f"{vault_url}.vault.azure.net"
    
    try:
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        client = SecretClient(vault_url=vault_url, credential=credential)
        
        # List secrets
        secrets = list(client.list_properties_of_secrets())
        secret_count = len(secrets)
        secret_names = [s.name for s in secrets[:5]]
        
        # Extract vault name from URL
        vault_name = vault_url.replace('https://', '').split('.')[0]
        
        return True, f"Successfully authenticated to Azure Key Vault\nVault: {vault_name}\nSecrets: {secret_count}\nSample: {', '.join(secret_names[:3])}{'...' if secret_count > 3 else ''}"
        
    except Exception as e:
        error_msg = str(e)
        if 'Unauthorized' in error_msg or '401' in error_msg:
            return False, "Authentication failed: Invalid credentials or insufficient permissions"
        return False, f"Azure Key Vault error: {e}"

