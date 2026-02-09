"""Configuration settings for VFR ATC Director Agent."""

import os
from typing import Optional


class Config:
    """Configuration settings for the VFR ATC simulation."""
    
    # Model Configuration
    MODEL_NAME = "gemini-2.5-flash-native-audio-preview-12-2025"
    MODEL_TIMEOUT = 300
    MODEL_MAX_RETRIES = 3
    
    # Audio Configuration
    AUDIO_SAMPLE_RATE = 16000  # 16kHz standard for speech
    AUDIO_CHANNELS = 1  # Mono for radio simulation
    AUDIO_CHUNK_SIZE = 1024
    AUDIO_FORMAT = "LINEAR16"  # PCM format
    
    # Simulation Settings
    AIRPORT_AGNOSTIC = True  # Can work with any airport configuration
    PHRASEOLOGY_STRICT = True  # Enforce realistic ATC phraseology
    TRAINING_MODE = False  # If True, provides educational feedback
    
    # API Configuration
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GOOGLE_PROJECT_ID: Optional[str] = os.getenv("GOOGLE_PROJECT_ID")
    
    # Director Settings
    ENABLE_SUB_AGENTS = True  # Enable delegation to specialist agents
    MAX_DELEGATION_DEPTH = 3  # Prevent infinite delegation loops
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_AUDIO_STREAMS = False  # Enable for debugging audio issues
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration settings.
        
        Raises:
            ValueError: If required settings are missing or invalid.
        """
        if not cls.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY environment variable is required. "
                "Set it with: export GOOGLE_API_KEY='your-api-key'"
            )
        
        if cls.MODEL_TIMEOUT <= 0:
            raise ValueError("MODEL_TIMEOUT must be positive")
        
        if cls.MODEL_MAX_RETRIES < 0:
            raise ValueError("MODEL_MAX_RETRIES must be non-negative")
        
        if cls.AUDIO_SAMPLE_RATE not in [8000, 16000, 24000, 48000]:
            raise ValueError(
                f"Unsupported AUDIO_SAMPLE_RATE: {cls.AUDIO_SAMPLE_RATE}. "
                "Use 8000, 16000, 24000, or 48000 Hz"
            )
    
    @classmethod
    def get_model_config(cls) -> dict:
        """Get model configuration dictionary.
        
        Returns:
            Dictionary with model configuration parameters.
        """
        return {
            "model": cls.MODEL_NAME,
            "timeout": cls.MODEL_TIMEOUT,
            "max_retries": cls.MODEL_MAX_RETRIES,
        }
    
    @classmethod
    def get_audio_config(cls) -> dict:
        """Get audio configuration dictionary.
        
        Returns:
            Dictionary with audio streaming parameters.
        """
        return {
            "sample_rate": cls.AUDIO_SAMPLE_RATE,
            "channels": cls.AUDIO_CHANNELS,
            "chunk_size": cls.AUDIO_CHUNK_SIZE,
            "format": cls.AUDIO_FORMAT,
        }
