"""Braintree/PayPal authentication module."""

module_description = "Braintree (Payment)"

form_fields = [
    {"name": "merchant_id", "type": "text", "label": "Merchant ID", "default": ""},
    {"name": "public_key", "type": "text", "label": "Public Key", "default": ""},
    {"name": "private_key", "type": "password", "label": "Private Key", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "production"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Braintree (PayPal). API keys from Braintree Control Panel."}
]

def authenticate(form_data):
    """Test Braintree authentication."""
    try:
        import braintree
        
        merchant_id = form_data.get("merchant_id", "")
        public_key = form_data.get("public_key", "")
        private_key = form_data.get("private_key", "")
        environment = form_data.get("environment", "sandbox")
        
        env = braintree.Environment.Sandbox if environment == "sandbox" else braintree.Environment.Production
        
        gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                environment=env,
                merchant_id=merchant_id,
                public_key=public_key,
                private_key=private_key
            )
        )
        
        # Test with a client token generation
        token = gateway.client_token.generate()
        
        if token:
            return True, f"Braintree authentication successful ({environment})"
        else:
            return False, "Failed to generate client token"
            
    except ImportError:
        return False, "braintree library not installed. Install with: pip install braintree"
    except Exception as e:
        return False, f"Braintree error: {str(e)}"

