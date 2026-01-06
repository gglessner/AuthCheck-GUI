"""Linkerd Service Mesh authentication module."""

module_description = "Linkerd (Middleware)"

form_fields = [
    {"name": "api_url", "type": "text", "label": "Kubernetes API URL", "default": "https://localhost:6443"},
    {"name": "token", "type": "password", "label": "Bearer Token", "default": ""},
    {"name": "kubeconfig", "type": "file", "label": "Kubeconfig File", "filter": "Config Files (*.yaml *.yml)"},
    {"name": "namespace", "type": "text", "label": "Linkerd Namespace", "default": "linkerd"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Uses Kubernetes auth. Check linkerd namespace. Dashboard on port 50750."}
]

def authenticate(form_data):
    """Test Linkerd/Kubernetes authentication."""
    try:
        from kubernetes import client, config
        
        kubeconfig = form_data.get("kubeconfig", "")
        token = form_data.get("token", "")
        api_url = form_data.get("api_url", "")
        namespace = form_data.get("namespace", "linkerd")
        verify_ssl = form_data.get("verify_ssl", True)
        
        if kubeconfig:
            config.load_kube_config(config_file=kubeconfig)
        elif token:
            configuration = client.Configuration()
            configuration.host = api_url
            configuration.verify_ssl = verify_ssl
            configuration.api_key = {"authorization": f"Bearer {token}"}
            client.Configuration.set_default(configuration)
        
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace=namespace)
        linkerd_pods = [p.metadata.name for p in pods.items]
        
        if linkerd_pods:
            return True, f"Linkerd found with {len(linkerd_pods)} pods in {namespace}"
        else:
            return False, f"No pods found in {namespace} namespace"
            
    except ImportError:
        return False, "kubernetes library not installed. Install with: pip install kubernetes"
    except Exception as e:
        return False, f"Linkerd error: {str(e)}"
