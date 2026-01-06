"""DICOM authentication module."""

module_description = "DICOM (Healthcare)"

form_fields = [
    {"name": "host", "type": "text", "label": "PACS Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "104"},
    {"name": "calling_ae", "type": "text", "label": "Calling AE Title", "default": "PYNETDICOM"},
    {"name": "called_ae", "type": "text", "label": "Called AE Title", "default": "ANY-SCP"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "DICOM uses AE Titles for identification. Default port 104 or 11112."}
]

def authenticate(form_data):
    """Test DICOM association."""
    try:
        from pynetdicom import AE, VerificationPresentationContexts
        
        host = form_data.get("host", "localhost")
        port = int(form_data.get("port", 104))
        calling_ae = form_data.get("calling_ae", "PYNETDICOM")
        called_ae = form_data.get("called_ae", "ANY-SCP")
        
        ae = AE(ae_title=calling_ae)
        ae.requested_contexts = VerificationPresentationContexts
        
        assoc = ae.associate(host, port, ae_title=called_ae)
        
        if assoc.is_established:
            # Send C-ECHO
            status = assoc.send_c_echo()
            assoc.release()
            
            if status:
                return True, f"DICOM C-ECHO successful to {called_ae}@{host}:{port}"
            else:
                return False, "C-ECHO failed"
        else:
            return False, f"Association rejected: {assoc.rejection_reason}"
            
    except ImportError:
        return False, "pynetdicom library not installed. Install with: pip install pynetdicom"
    except Exception as e:
        return False, f"DICOM error: {str(e)}"

