"""Main entry point for PR review swarm."""

from config import MODEL_NAME, GITHUB_OWNER, GITHUB_REPO, GITHUB_PR_NUMBER, validate_api_key
from infrastructure.github import fetch_github_pr, GitHubClient
from services import run_pr_review


def main():
    """Main entry point."""
    # Validate API key based on model
    validate_api_key(MODEL_NAME)
    
    # Fetch PR from GitHub
    try:
        print(f"\n🔍 Fetching PR #{GITHUB_PR_NUMBER} from {GITHUB_OWNER}/{GITHUB_REPO}...\n")
        pr_data = fetch_github_pr(GITHUB_OWNER, GITHUB_REPO, GITHUB_PR_NUMBER)
        
        # Format for display
        client = GitHubClient()
        pr_summary = client.format_pr_summary(pr_data)
        print(pr_summary)
        print("\n" + "="*80 + "\n")
        
        # Run review with GitHub data
        result = run_pr_review(
            pr_number=str(pr_data.number),
            pr_description=f"{pr_data.title}\n\n{pr_data.description}",
            pr_diff=pr_data.diff,
            model_name=MODEL_NAME
        )
    except Exception as e:
        print(f"❌ Failed to fetch PR from GitHub: {e}")
        print("Make sure GITHUB_TOKEN is set in .env file")
        return
    
    if result['success']:
        print(f"\n✅ Review complete! Report saved to: {result['report_path']}")


if __name__ == "__main__":
    main()
