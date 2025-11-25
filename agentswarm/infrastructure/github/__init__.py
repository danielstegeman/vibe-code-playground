"""GitHub integration package."""

from .client import GitHubClient, PullRequestData, fetch_github_pr

__all__ = ['GitHubClient', 'PullRequestData', 'fetch_github_pr']
