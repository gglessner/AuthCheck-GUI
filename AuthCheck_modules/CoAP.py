"""CoAP (Constrained Application Protocol) authentication module."""

module_description = "CoAP (IoT)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "5683"},
    {"name": "path", "type": "text", "label": "Resource Path", "default": "/.well-known/core"},
    {"name": "use_dtls", "type": "checkbox", "label": "Use DTLS", "default": False},
    {"name": "psk_identity", "type": "text", "label": "PSK Identity", "default": ""},
    {"name": "psk_key", "type": "password", "label": "PSK Key", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "CoAP port 5683, CoAPs (DTLS) port 5684. No standard auth."}
]

def authenticate(form_data):
    """Test CoAP connection."""
    try:
        from aiocoap import Context, Message, GET
        import asyncio
        
        host = form_data.get("host", "localhost")
        port = form_data.get("port", "5683")
        path = form_data.get("path", "/.well-known/core")
        
        async def coap_request():
            context = await Context.create_client_context()
            
            uri = f"coap://{host}:{port}{path}"
            request = Message(code=GET, uri=uri)
            
            response = await context.request(request).response
            return response
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(coap_request())
        loop.close()
        
        if response.code.is_successful():
            return True, f"CoAP connection successful to {host}:{port}"
        else:
            return False, f"CoAP error: {response.code}"
            
    except ImportError:
        return False, "aiocoap library not installed. Install with: pip install aiocoap"
    except Exception as e:
        return False, f"CoAP error: {str(e)}"

