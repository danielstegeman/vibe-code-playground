"""Core utilities."""

import time
from pathlib import Path
from typing import Callable, TypeVar, Any
from functools import wraps


# Minimal placeholder prompt for testing (conserves tokens)
MINIMAL_PROMPT = "You are a code reviewer. Provide a brief review response."


T = TypeVar('T')


def _is_rate_limit_error(exception: Exception) -> bool:
    """
    Check if the exception is a rate limit error.
    
    Args:
        exception: The exception to check
        
    Returns:
        True if this is a rate limit error, False otherwise
    """
    error_str = str(exception).lower()
    error_type = type(exception).__name__
    
    # Check for common rate limit indicators
    rate_limit_indicators = [
        'rate_limit_error',
        'ratelimiterror',
        'rate limit',
        'too many requests',
        '429',
        'quota exceeded',
        'tokens per minute'
    ]
    
    return any(indicator in error_str for indicator in rate_limit_indicators)


def exponential_backoff_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,),
    log_callback: Callable[[str], None] = None
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.
    
    Implements exponential backoff retry pattern for handling transient failures:
    - Retry 1: wait base_delay seconds
    - Retry 2: wait base_delay * exponential_base seconds
    - Retry 3: wait base_delay * exponential_base^2 seconds
    - etc.
    
    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay between retries in seconds (default: 1.0)
        max_delay: Maximum delay between retries in seconds (default: 60.0)
        exponential_base: Multiplier for exponential backoff (default: 2.0)
        exceptions: Tuple of exception types to catch and retry (default: all exceptions)
        log_callback: Optional callback function for logging retry attempts
        
    Returns:
        Decorated function with retry logic
        
    Example:
        @exponential_backoff_retry(max_retries=3, base_delay=1.0)
        def call_api():
            return agent.run("task")
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    # Detect if this is a rate limit error
                    is_rate_limit = _is_rate_limit_error(e)
                    
                    # Don't retry if we've exhausted attempts
                    if attempt >= max_retries:
                        if log_callback:
                            error_type = "Rate limit error" if is_rate_limit else "Error"
                            log_callback(
                                f"{error_type} - Failed after {max_retries} retries: {type(e).__name__}"
                            )
                        raise
                    
                    # Calculate exponential backoff delay
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    # Enhanced logging for rate limit errors
                    if log_callback:
                        if is_rate_limit:
                            log_callback(
                                f"WARNING: Rate limit exceeded (attempt {attempt + 1}/{max_retries}). "
                                f"Waiting {delay:.1f}s before retry..."
                            )
                        else:
                            log_callback(
                                f"Attempt {attempt + 1}/{max_retries} failed: {type(e).__name__}. "
                                f"Retrying in {delay:.1f}s..."
                            )
                    
                    time.sleep(delay)
            
            # Should never reach here, but for type safety
            raise last_exception
        
        return wrapper
    return decorator


def retry_agent_execution(
    agent: Any,
    task: str,
    max_retries: int = 3,
    base_delay: float = 1.0,
    log_callback: Callable[[str], None] = None,
    **kwargs: Any
) -> str:
    """
    Execute an agent with exponential backoff retry logic.
    
    Wraps agent.run() calls with automatic retry on failures.
    Useful for handling transient API errors, rate limits, and network issues.
    
    Args:
        agent: The agent instance to execute
        task: The task string to pass to agent.run()
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay between retries in seconds (default: 1.0)
        log_callback: Optional callback for logging retry attempts
        **kwargs: Additional keyword arguments to pass to agent.run()
        
    Returns:
        The agent's response as a string
        
    Raises:
        The last exception encountered if all retries fail
        
    Example:
        response = retry_agent_execution(
            agent=my_agent,
            task="Review this code",
            max_retries=3,
            log_callback=logger.log_progress
        )
    """
    @exponential_backoff_retry(
        max_retries=max_retries,
        base_delay=base_delay,
        log_callback=log_callback
    )
    def _execute():
        return agent.run(task, **kwargs)
    
    return _execute()


def load_prompt_from_file(prompt_path: Path) -> str:
    """
    Load a prompt from a markdown file.
    Automatically uses minimal prompt if MINIMAL_TOKEN_MODE is enabled.
    
    Args:
        prompt_path: Path to the prompt markdown file
        
    Returns:
        The prompt text as a string (or minimal prompt if in minimal token mode)
    """
    # Lazy import to avoid circular dependency
    from config import MINIMAL_TOKEN_MODE
    
    if MINIMAL_TOKEN_MODE:
        return MINIMAL_PROMPT
    return prompt_path.read_text(encoding='utf-8')
