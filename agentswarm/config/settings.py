"""Configuration settings for PR review swarm."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# ============================================================================
# DEVELOPMENT CONFIGURATION
# ============================================================================

# Minimal token mode - replaces agent prompts with minimal placeholders to conserve tokens during testing
MINIMAL_TOKEN_MODE = os.getenv("MINIMAL_TOKEN_MODE", "false").lower() in ("true", "1", "yes")


# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# Supported models:
# - OpenAI: "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"
# - Anthropic: "anthropic/claude-3-opus-20240229", "anthropic/claude-3-sonnet-20240229"
# - Groq: "groq/llama-3.1-70b-versatile", "groq/mixtral-8x7b-32768"
# - Cohere: "cohere/command-r-plus", "cohere/command-r"
# - DeepSeek: "deepseek/deepseek-chat", "deepseek/deepseek-coder"
# - Gemini: "gemini/gemini-pro", "gemini/gemini-1.5-pro"

MODEL_NAME = os.getenv("MODEL_NAME", "anthropic/claude-sonnet-4-5")


# ============================================================================
# GITHUB CONFIGURATION
# ============================================================================

GITHUB_OWNER = os.getenv("GITHUB_OWNER", "danielstegeman")
GITHUB_REPO = os.getenv("GITHUB_REPO", "vibe-code-playground")
GITHUB_PR_NUMBER = int(os.getenv("GITHUB_PR_NUMBER", "1"))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs/reports")


# ============================================================================
# API KEY VALIDATION
# ============================================================================

def validate_api_key(model_name: str = None) -> None:
    """
    Validate that the required API key is present for the specified model.
    
    Args:
        model_name: The model name to validate. If None, uses MODEL_NAME from config.
        
    Raises:
        SystemExit: If the required API key is not found.
    """
    if model_name is None:
        model_name = MODEL_NAME
    
    model_provider_map = {
        'gpt-': 'OPENAI_API_KEY',
        'anthropic/': 'ANTHROPIC_API_KEY',
        'groq/': 'GROQ_API_KEY',
        'cohere/': 'COHERE_API_KEY',
        'deepseek/': 'DEEPSEEK_API_KEY',
        'gemini/': 'GEMINI_API_KEY',
    }
    
    required_key = None
    for prefix, key_name in model_provider_map.items():
        if model_name.startswith(prefix):
            required_key = key_name
            break
    
    # Default to OpenAI if no prefix matches
    if not required_key:
        required_key = 'OPENAI_API_KEY'
    
    if not os.getenv(required_key):
        print(f"❌ ERROR: {required_key} not found in environment variables")
        print(f"Please create a .env file with your API key for model: {model_name}")
        print("See .env.example for all supported providers")
        exit(1)


def get_github_config() -> dict:
    """
    Get GitHub configuration as a dictionary.
    
    Returns:
        Dictionary with GitHub configuration values.
    """
    return {
        'owner': GITHUB_OWNER,
        'repo': GITHUB_REPO,
        'pr_number': GITHUB_PR_NUMBER,
        'token': GITHUB_TOKEN
    }
