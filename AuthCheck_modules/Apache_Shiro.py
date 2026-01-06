# Apache Shiro Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Shiro (IAM)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8080",
     "port_toggle": "use_https", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "login_path", "type": "text", "label": "Login Path", "default": "/login"},
    {"name": "use_https", "type": "checkbox", "label": "Use HTTPS"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "remember_me", "type": "checkbox", "label": "Remember Me"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 8443, Non-TLS: 8080. Shiro framework - app-specific."},
]


def authenticate(form_data):
    """
    Attempt to authenticate to an Apache Shiro protected application.
    """
    try:
        import requests
    except ImportError:
        return False, "requests package not installed. Run: pip install requests"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    login_path = form_data.get('login_path', '/login').strip()
    use_https = form_data.get('use_https', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    remember_me = form_data.get('remember_me', False)
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        scheme = "https" if use_https else "http"
        port_num = port if port else "8080"
        base_url = f"{scheme}://{host}:{port_num}"
        
        session = requests.Session()
        
        # Get login page first (for CSRF token if any)
        login_page = session.get(f"{base_url}{login_path}", verify=verify_ssl, timeout=10)
        
        # Attempt login
        login_data = {
            "username": username,
            "password": password,
        }
        if remember_me:
            login_data["rememberMe"] = "true"
        
        response = session.post(f"{base_url}{login_path}", data=login_data, verify=verify_ssl, timeout=10, allow_redirects=False)
        
        # Shiro typically redirects on success
        if response.status_code in [302, 303]:
            redirect_location = response.headers.get('Location', '')
            
            # Check for error indicators in redirect
            if 'error' in redirect_location.lower() or 'login' in redirect_location.lower():
                return False, "Authentication failed: Redirected back to login"
            
            # Check cookies for Shiro session
            cookies = session.cookies.get_dict()
            has_session = any('JSESSIONID' in k or 'rememberMe' in k for k in cookies.keys())
            
            if has_session or redirect_location:
                return True, f"Successfully authenticated to Shiro-protected app at {host}:{port_num}\nRedirected to: {redirect_location}"
        elif response.status_code == 200:
            # Check if login form is still present (failed) or if we got a different page (success)
            if 'login' in response.text.lower() and ('password' in response.text.lower() or 'error' in response.text.lower()):
                return False, "Authentication failed: Invalid credentials"
            return True, f"Successfully authenticated to Shiro-protected app at {host}:{port_num}"
        elif response.status_code == 401:
            return False, "Authentication failed: Unauthorized"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Shiro error: {e}"

