"""OpenShift authentication module."""

module_description = "OpenShift (Container)"

form_fields = [
    {"name": "api_url", "type": "text", "label": "API URL", "default": "https://api.cluster.example.com:6443"},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["Token", "Username/Password", "Kubeconfig"], "default": "Token"},
    {"name": "token", "type": "password", "label": "Bearer Token", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "kubeconfig", "type": "file", "label": "Kubeconfig File", "filter": "Config Files (*.yaml *.yml *.conf)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Get token: oc whoami -t. Default kubeadmin user on new clusters."}
]

def authenticate(form_data):
    """Test OpenShift authentication."""
    try:
        from kubernetes import client, config
        from openshift.dynamic import DynamicClient
        
        api_url = form_data.get("api_url", "")
        auth_type = form_data.get("auth_type", "Token")
        token = form_data.get("token", "")
        kubeconfig = form_data.get("kubeconfig", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        if auth_type == "Kubeconfig" and kubeconfig:
            config.load_kube_config(config_file=kubeconfig)
        else:
            configuration = client.Configuration()
            configuration.host = api_url
            configuration.verify_ssl = verify_ssl
            configuration.api_key = {"authorization": f"Bearer {token}"}
            client.Configuration.set_default(configuration)
        
        k8s_client = client.ApiClient()
        dyn_client = DynamicClient(k8s_client)
        
        # Test by getting projects
        projects = dyn_client.resources.get(api_version="project.openshift.io/v1", kind="Project")
        project_list = projects.get()
        
        return True, f"OpenShift authentication successful ({len(project_list.items)} projects)"
        
    except ImportError:
        return False, "openshift library not installed. Install with: pip install openshift"
    except Exception as e:
        return False, f"OpenShift error: {str(e)}"
