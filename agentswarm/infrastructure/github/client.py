"""GitHub API client for fetching pull request data."""

import os
import requests
from typing import Optional
from dataclasses import dataclass


@dataclass
class PullRequestData:
    """Data structure for GitHub pull request information."""
    number: int
    title: str
    description: str
    diff: str
    files_changed: list[dict]
    author: str
    base_branch: str
    head_branch: str
    state: str
    url: str


class GitHubClient:
    """Client for interacting with GitHub API to fetch PR data."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub client.
        
        Args:
            token: GitHub personal access token. If not provided, will try to load from GITHUB_TOKEN env var.
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN environment variable or pass token parameter.")
        
        self.base_url = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def get_pull_request(self, owner: str, repo: str, pr_number: int) -> PullRequestData:
        """
        Fetch pull request data from GitHub.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            pr_number: Pull request number
            
        Returns:
            PullRequestData object with all PR information
            
        Raises:
            requests.HTTPError: If the API request fails
        """
        # Get PR metadata
        pr_url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        response = requests.get(pr_url, headers=self.headers)
        response.raise_for_status()
        pr_data = response.json()
        
        # Get PR diff
        diff = self._get_pr_diff(owner, repo, pr_number)
        
        # Get changed files
        files = self._get_pr_files(owner, repo, pr_number)
        
        return PullRequestData(
            number=pr_data['number'],
            title=pr_data['title'],
            description=pr_data['body'] or '',
            diff=diff,
            files_changed=files,
            author=pr_data['user']['login'],
            base_branch=pr_data['base']['ref'],
            head_branch=pr_data['head']['ref'],
            state=pr_data['state'],
            url=pr_data['html_url']
        )
    
    def _get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """Fetch the diff content for a pull request."""
        diff_url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        headers = {**self.headers, 'Accept': 'application/vnd.github.v3.diff'}
        
        response = requests.get(diff_url, headers=headers)
        response.raise_for_status()
        
        return response.text
    
    def _get_pr_files(self, owner: str, repo: str, pr_number: int) -> list[dict]:
        """Fetch the list of changed files in a pull request."""
        files_url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        
        response = requests.get(files_url, headers=self.headers)
        response.raise_for_status()
        
        files_data = response.json()
        
        return [
            {
                'filename': file['filename'],
                'status': file['status'],
                'additions': file['additions'],
                'deletions': file['deletions'],
                'changes': file['changes'],
                'patch': file.get('patch', '')
            }
            for file in files_data
        ]
    
    def format_pr_summary(self, pr_data: PullRequestData) -> str:
        """
        Format pull request data into a readable summary for agent consumption.
        
        Args:
            pr_data: PullRequestData object
            
        Returns:
            Formatted string summary of the PR
        """
        files_summary = '\n'.join([
            f"  - {f['filename']} ({f['status']}: +{f['additions']} -{f['deletions']})"
            for f in pr_data.files_changed
        ])
        
        summary = f"""Pull Request #{pr_data.number}: {pr_data.title}

Author: {pr_data.author}
Branch: {pr_data.head_branch} → {pr_data.base_branch}
State: {pr_data.state}
URL: {pr_data.url}

Description:
{pr_data.description}

Files Changed ({len(pr_data.files_changed)} files):
{files_summary}
"""
        return summary


def fetch_github_pr(owner: str, repo: str, pr_number: int, token: Optional[str] = None) -> PullRequestData:
    """
    Convenience function to fetch GitHub PR data.
    
    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number
        token: Optional GitHub token (uses GITHUB_TOKEN env var if not provided)
        
    Returns:
        PullRequestData object
    """
    client = GitHubClient(token=token)
    return client.get_pull_request(owner, repo, pr_number)
