"""VxWorks RTOS authentication module."""

module_description = "VxWorks (RTOS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": ""},
    {"name": "port", "type": "text", "label": "FTP/Telnet Port", "default": "21"},
    {"name": "username", "type": "text", "label": "Username", "default": "target"},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "protocol", "type": "combo", "label": "Protocol", "options": ["FTP", "Telnet", "SSH"], "default": "FTP"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Common defaults: target/password, admin/admin. FTP port 21, Telnet 23."}
]

def authenticate(form_data):
    """Test VxWorks authentication."""
    try:
        from ftplib import FTP
        import telnetlib
        import socket
        
        host = form_data.get("host", "")
        port = int(form_data.get("port", 21))
        username = form_data.get("username", "target")
        password = form_data.get("password", "")
        protocol = form_data.get("protocol", "FTP")
        
        if protocol == "FTP":
            ftp = FTP()
            ftp.connect(host, port, timeout=30)
            ftp.login(username, password)
            ftp.quit()
            return True, f"VxWorks FTP authentication successful"
            
        elif protocol == "Telnet":
            tn = telnetlib.Telnet(host, port, timeout=30)
            tn.read_until(b"login: ", timeout=10)
            tn.write(username.encode() + b"\n")
            tn.read_until(b"Password: ", timeout=10)
            tn.write(password.encode() + b"\n")
            response = tn.read_some().decode()
            tn.close()
            
            if ">" in response or "->" in response:
                return True, f"VxWorks Telnet authentication successful"
            else:
                return False, "Authentication failed"
        else:
            return False, f"Protocol {protocol} not implemented"
            
    except Exception as e:
        return False, f"VxWorks error: {str(e)}"

