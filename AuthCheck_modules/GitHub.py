# GitHub Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "GitHub (CI/CD)"

form_fields = [
    {"name": "token", "type": "password", "label": "Personal Access Token"},
    {"name": "enterprise_url", "type": "text", "label": "Enterprise URL (Optional)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "PAT from Settings > Developer settings > Personal access tokens. Enterprise URL for GitHub Enterprise Server."},
]


def authenticate(form_data):
    """Attempt to authenticate to GitHub."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    token = form_data.get('token', '').strip()
    enterprise_url = form_data.get('enterprise_url', '').strip()
    
    if not token:
        return False, "Personal Access Token is required"
    
    try:
        if enterprise_url:
            if not enterprise_url.startswith('http'):
                enterprise_url = f"https://{enterprise_url}"
            base_url = f"{enterprise_url.rstrip('/')}/api/v3"
        else:
            base_url = "https://api.github.com"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        
        # Get user info
        response = requests.get(f"{base_url}/user",
                               headers=headers, timeout=15)
        
        if response.status_code == 200:
            user = response.json()
            username = user.get('login', 'unknown')
            user_type = user.get('type', 'User')
            
            # Get repo count
            repos_resp = requests.get(f"{base_url}/user/repos?per_page=1",
                                     headers=headers, timeout=10)
            repo_count = 0
            if repos_resp.status_code == 200:
                # Check Link header for total
                link_header = repos_resp.headers.get('Link', '')
                if 'last' in link_header:
                    import re
                    match = re.search(r'page=(\d+)>; rel="last"', link_header)
                    if match:
                        repo_count = int(match.group(1))
                else:
                    repo_count = len(repos_resp.json())
            
            # Get org count
            orgs_resp = requests.get(f"{base_url}/user/orgs",
                                    headers=headers, timeout=10)
            org_count = 0
            org_names = []
            if orgs_resp.status_code == 200:
                orgs = orgs_resp.json()
                org_count = len(orgs)
                org_names = [o['login'] for o in orgs[:3]]
            
            platform = "GitHub Enterprise" if enterprise_url else "GitHub"
            return True, f"Successfully authenticated to {platform}\nUser: {username} ({user_type})\nRepositories: {repo_count}\nOrganizations: {org_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid token"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"GitHub error: {e}"

