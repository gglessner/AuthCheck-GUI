"""Istio Service Mesh authentication module."""

module_description = "Istio (Middleware)"

form_fields = [
    {"name": "api_url", "type": "text", "label": "Kubernetes API URL", "default": "https://localhost:6443"},
    {"name": "token", "type": "password", "label": "Bearer Token", "default": ""},
    {"name": "kubeconfig", "type": "file", "label": "Kubeconfig File", "filter": "Config Files (*.yaml *.yml)"},
    {"name": "namespace", "type": "text", "label": "Istio Namespace", "default": "istio-system"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Uses Kubernetes auth. Check istio-system namespace for Istio resources."}
]

def authenticate(form_data):
    """Test Istio/Kubernetes authentication."""
    try:
        from kubernetes import client, config
        
        kubeconfig = form_data.get("kubeconfig", "")
        token = form_data.get("token", "")
        api_url = form_data.get("api_url", "")
        namespace = form_data.get("namespace", "istio-system")
        verify_ssl = form_data.get("verify_ssl", True)
        
        if kubeconfig:
            config.load_kube_config(config_file=kubeconfig)
        elif token:
            configuration = client.Configuration()
            configuration.host = api_url
            configuration.verify_ssl = verify_ssl
            configuration.api_key = {"authorization": f"Bearer {token}"}
            client.Configuration.set_default(configuration)
        else:
            config.load_incluster_config()
        
        v1 = client.CoreV1Api()
        
        # Check for Istio pods
        pods = v1.list_namespaced_pod(namespace=namespace)
        istio_pods = [p.metadata.name for p in pods.items if 'istio' in p.metadata.name]
        
        if istio_pods:
            return True, f"Istio found with {len(istio_pods)} pods in {namespace}"
        else:
            return True, f"K8s auth successful but no Istio pods found in {namespace}"
            
    except ImportError:
        return False, "kubernetes library not installed. Install with: pip install kubernetes"
    except Exception as e:
        return False, f"Istio error: {str(e)}"
