"""HashiCorp Nomad authentication module."""

module_description = "HashiCorp Nomad (Container)"

form_fields = [
    {"name": "address", "type": "text", "label": "Nomad Address", "default": "http://localhost:4646"},
    {"name": "token", "type": "password", "label": "ACL Token", "default": ""},
    {"name": "namespace", "type": "text", "label": "Namespace", "default": "default"},
    {"name": "region", "type": "text", "label": "Region", "default": "global"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Bootstrap token from 'nomad acl bootstrap'. Port 4646 HTTP, 4647 RPC."}
]

def authenticate(form_data):
    """Test Nomad authentication."""
    try:
        import nomad
        
        address = form_data.get("address", "http://localhost:4646")
        token = form_data.get("token", "")
        namespace = form_data.get("namespace", "default")
        region = form_data.get("region", "global")
        verify_ssl = form_data.get("verify_ssl", True)
        
        n = nomad.Nomad(
            host=address.replace("http://", "").replace("https://", "").split(":")[0],
            secure=address.startswith("https"),
            token=token if token else None,
            namespace=namespace,
            region=region,
            verify=verify_ssl
        )
        
        # Test by getting agent info
        agent = n.agent.get_agent()
        
        return True, f"Nomad authentication successful (Region: {agent.get('config', {}).get('Region', 'unknown')})"
        
    except ImportError:
        return False, "python-nomad library not installed. Install with: pip install python-nomad"
    except Exception as e:
        return False, f"Nomad error: {str(e)}"

