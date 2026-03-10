import requests

def github_repo_info(owner: str, repo: str) -> str:
    """Fetches high-level metadata (stars, forks, open issues, language) for a GitHub repository."""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}"
        # Public API request - no authentication required for low volume requests
        res = requests.get(url, timeout=10)
        
        if res.status_code == 404:
            return f"Repository '{owner}/{repo}' not found. Check spelling."
            
        res.raise_for_status()
        data = res.json()
        
        output = f"--- GITHUB METADATA for '{owner}/{repo}' ---\n"
        output += f"Description: {data.get('description', 'No description.')}\n"
        output += f"Primary Language: {data.get('language')}\n"
        output += f"Stars: {data.get('stargazers_count', 0):,}\n"
        output += f"Forks: {data.get('forks_count', 0):,}\n"
        output += f"Open Issues (incl. PRs): {data.get('open_issues_count', 0):,}\n"
        output += f"Last Updated at: {data.get('updated_at')}\n"
        output += f"Default Branch: {data.get('default_branch')}\n"
        output += f"License: {data.get('license', {}).get('name') if data.get('license') else 'None'}\n"
        
        return output
    except Exception as e:
        return f"Error fetching GitHub repo metadata: {str(e)}"
