"""QNX RTOS authentication module."""

module_description = "QNX (RTOS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": ""},
    {"name": "port", "type": "text", "label": "SSH Port", "default": "22"},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Common defaults: root/root. QNX Neutrino uses standard SSH."}
]

def authenticate(form_data):
    """Test QNX authentication."""
    try:
        import paramiko
        
        host = form_data.get("host", "")
        port = int(form_data.get("port", 22))
        username = form_data.get("username", "root")
        password = form_data.get("password", "")
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=30,
            allow_agent=False,
            look_for_keys=False
        )
        
        # Verify it's QNX
        stdin, stdout, stderr = client.exec_command("uname -s")
        os_name = stdout.read().decode().strip()
        
        client.close()
        
        if "QNX" in os_name:
            return True, f"QNX authentication successful (OS: {os_name})"
        else:
            return True, f"SSH authentication successful (OS: {os_name})"
            
    except ImportError:
        return False, "paramiko library not installed. Install with: pip install paramiko"
    except Exception as e:
        return False, f"QNX error: {str(e)}"

