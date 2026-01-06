"""IBM TSO/ISPF authentication module."""

module_description = "IBM TSO/ISPF (Mainframe)"

form_fields = [
    {"name": "host", "type": "text", "label": "z/OS Host", "default": ""},
    {"name": "port", "type": "text", "label": "TN3270 Port", "default": "23",
     "port_toggle": "use_ssl", "tls_port": "992", "non_tls_port": "23"},
    {"name": "userid", "type": "text", "label": "TSO User ID", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "use_ssl", "type": "checkbox", "label": "Use TN3270E SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 992, Non-TLS: 23. TN3270. RACF/ACF2/TSS auth."}
]

def authenticate(form_data):
    """Test TSO authentication via TN3270."""
    try:
        from py3270 import Emulator
        
        host = form_data.get("host", "")
        port = form_data.get("port", "23")
        userid = form_data.get("userid", "")
        password = form_data.get("password", "")
        use_ssl = form_data.get("use_ssl", False)
        
        em = Emulator(visible=False)
        
        if use_ssl:
            em.connect(f"L:{host}:{port}")
        else:
            em.connect(f"{host}:{port}")
        
        em.wait_for_field()
        
        # Send userid
        em.send_string(userid)
        em.send_enter()
        em.wait_for_field()
        
        # Send password
        em.send_string(password)
        em.send_enter()
        em.wait_for_field()
        
        screen = em.string_get(1, 1, 80)
        em.terminate()
        
        if "READY" in screen.upper() or "TSO" in screen.upper():
            return True, f"TSO authentication successful for {userid}"
        else:
            return False, f"TSO login failed"
            
    except ImportError:
        return False, "py3270 library not installed. Install with: pip install py3270"
    except Exception as e:
        return False, f"TSO error: {str(e)}"

