"""Docker Swarm authentication module."""

module_description = "Docker Swarm (Container)"

form_fields = [
    {"name": "host", "type": "text", "label": "Docker Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "2376",
     "port_toggle": "use_tls", "tls_port": "2376", "non_tls_port": "2375"},
    {"name": "use_tls", "type": "checkbox", "label": "Use TLS", "default": True},
    {"name": "cert_path", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.crt)"},
    {"name": "key_path", "type": "file", "label": "Client Key", "filter": "Key Files (*.pem *.key)"},
    {"name": "ca_cert", "type": "file", "label": "CA Certificate", "filter": "Certificate Files (*.pem *.crt)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 2376, Non-TLS: 2375. Certs in ~/.docker/"}
]

def authenticate(form_data):
    """Test Docker Swarm authentication."""
    try:
        import docker
        
        host = form_data.get("host", "localhost")
        port = form_data.get("port", "2376")
        use_tls = form_data.get("use_tls", True)
        cert_path = form_data.get("cert_path", "")
        key_path = form_data.get("key_path", "")
        ca_cert = form_data.get("ca_cert", "")
        
        if use_tls and cert_path and key_path:
            tls_config = docker.tls.TLSConfig(
                client_cert=(cert_path, key_path),
                ca_cert=ca_cert if ca_cert else None,
                verify=True
            )
            client = docker.DockerClient(
                base_url=f"tcp://{host}:{port}",
                tls=tls_config
            )
        else:
            client = docker.DockerClient(base_url=f"tcp://{host}:{port}")
        
        # Check if it's a swarm
        info = client.info()
        
        if info.get("Swarm", {}).get("LocalNodeState") == "active":
            nodes = client.nodes.list()
            return True, f"Docker Swarm authentication successful ({len(nodes)} nodes)"
        else:
            return True, f"Docker connection successful (not in swarm mode)"
            
    except ImportError:
        return False, "docker library not installed. Install with: pip install docker"
    except Exception as e:
        return False, f"Docker Swarm error: {str(e)}"

