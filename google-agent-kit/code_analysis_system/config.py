"""Configuration for the code analysis system."""

import os
from pathlib import Path


class Config:
    """Configuration settings for the multi-agent system."""
    
    # LLM settings
    MODEL_NAME = "anthropic/claude-sonnet-4-5-20250929"
    MODEL_TIMEOUT = 300  # 5 minutes
    MODEL_MAX_RETRIES = 3
    
    # Repository settings
    BASE_DIR = Path(__file__).parent.parent
    LINUX_REPO_PATH = BASE_DIR / "linux_repo"
    INDEX_OUTPUT_PATH = BASE_DIR / "outputs" / "indexes"
    
    # Agent settings
    MAX_LINES_PER_SUBDOMAIN_AGENT = 100000  # 100K LOC per agent
    MAX_FILE_READ_LINES = 1000  # Max lines to read from a single file at once
    MAX_SEARCH_RESULTS = 50
    
    # Orchestration settings
    ENABLE_PARALLEL_SUBDOMAIN_AGENTS = False  # Future: run agents in parallel
    MAX_SUBDOMAIN_AGENTS = 10  # Limit for safety
    
    @classmethod
    def validate(cls):
        """Validate configuration settings."""
        if not cls.LINUX_REPO_PATH.exists():
            print(f"Warning: Linux repository not found at {cls.LINUX_REPO_PATH}")
        
        if not cls.INDEX_OUTPUT_PATH.exists():
            print(f"Warning: Index directory not found at {cls.INDEX_OUTPUT_PATH}")
        
        return True


# Validate on import
Config.validate()
