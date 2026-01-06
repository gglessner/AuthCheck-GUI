"""Google Cloud IoT Core authentication module."""

module_description = "Google Cloud IoT Core (Cloud)"

form_fields = [
    {"name": "project_id", "type": "text", "label": "Project ID", "default": ""},
    {"name": "region", "type": "text", "label": "Region", "default": "us-central1"},
    {"name": "registry_id", "type": "text", "label": "Registry ID", "default": ""},
    {"name": "credentials_file", "type": "file", "label": "Service Account JSON", "filter": "JSON Files (*.json)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Uses service account credentials. IoT Core being deprecated - consider alternatives."}
]

def authenticate(form_data):
    """Test Google Cloud IoT authentication."""
    try:
        from google.cloud import iot_v1
        from google.oauth2 import service_account
        
        project_id = form_data.get("project_id", "")
        region = form_data.get("region", "us-central1")
        registry_id = form_data.get("registry_id", "")
        credentials_file = form_data.get("credentials_file", "")
        
        if credentials_file:
            credentials = service_account.Credentials.from_service_account_file(credentials_file)
            client = iot_v1.DeviceManagerClient(credentials=credentials)
        else:
            client = iot_v1.DeviceManagerClient()
        
        parent = f"projects/{project_id}/locations/{region}/registries/{registry_id}"
        
        # List devices
        devices = list(client.list_devices(parent=parent))
        
        return True, f"Google Cloud IoT auth successful ({len(devices)} devices in registry)"
        
    except ImportError:
        return False, "google-cloud-iot library not installed. Install with: pip install google-cloud-iot"
    except Exception as e:
        return False, f"Google Cloud IoT error: {str(e)}"

