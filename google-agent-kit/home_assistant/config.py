"""Configuration for the Home Assistant Multi-Agent System."""

import os


class Config:
    """Centralized configuration for the home assistant agents."""

    MODEL_NAME = os.environ.get(
        "HOME_ASSISTANT_MODEL", "gemini-2.0-flash"
    )
    APP_NAME = "home_assistant"
    USER_ID = "user_001"
