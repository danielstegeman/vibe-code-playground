"""Configuration for Monty Python Improv System"""


class Config:
    """Configuration settings for the improv system"""
    
    MODEL_NAME = "anthropic/claude-haiku-4-5-20251001"
    MODEL_TIMEOUT = 300
    MODEL_MAX_RETRIES = 3
    TPM = 50000  # Tokens per minute (org limit: 50,000 input TPM, buffer for concurrent requests)
    
    MIN_TURNS = 2
    MAX_TURNS = 5
    
    PERFORMERS = [
        'john_agent',
        'graham_agent',
        'terry_j_agent',
        'terry_g_agent',
        'eric_agent',
        'michael_agent'
    ]
