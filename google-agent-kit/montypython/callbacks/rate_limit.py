"""Rate limiting callback for API requests"""

import logging
import time

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Rate limit configuration
# Based on 50,000 input TPM org limit with safety buffer
RATE_LIMIT_SECS = 60  # Time window in seconds
RPM_QUOTA = 20  # Requests per minute quota
TPM_QUOTA = 30000  # Tokens per minute quota (with 10k buffer from 50k org limit)


def _estimate_tokens(llm_request: LlmRequest) -> int:
    """Estimate token count for the request.
    
    Uses a simple heuristic: ~4 characters per token.
    This is an approximation but works reasonably well for rate limiting.
    
    Args:
        llm_request: The LLM request to estimate tokens for.
        
    Returns:
        Estimated token count.
    """
    total_chars = 0
    
    for content in llm_request.contents:
        for part in content.parts:
            if part.text:
                total_chars += len(part.text)
    
    # Rough estimate: 4 chars per token
    estimated_tokens = total_chars // 4
    return max(estimated_tokens, 1)  # Minimum 1 token


def rate_limit_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> None:
    """Callback function that implements request and token rate limiting.
    
    This callback tracks both requests and tokens across all agents sharing 
    the same session state. It enforces limits by sleeping when either quota 
    is exceeded.
    
    Args:
        callback_context: A CallbackContext object representing the active
                         callback context.
        llm_request: A LlmRequest object representing the active LLM request.
    """
    # Handle empty text parts
    for content in llm_request.contents:
        for part in content.parts:
            if part.text == "":
                part.text = " "
    
    # Estimate tokens for this request
    estimated_tokens = _estimate_tokens(llm_request)
    
    now = time.time()
    
    # Initialize rate limit tracking on first request
    if "timer_start" not in callback_context.state:
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
        callback_context.state["token_count"] = estimated_tokens
        logger.debug(
            "rate_limit_callback [timestamp: %i, req_count: 1, token_count: %i, elapsed_secs: 0]",
            now,
            estimated_tokens,
        )
        return
    
    # Track current request and tokens
    request_count = callback_context.state["request_count"] + 1
    token_count = callback_context.state["token_count"] + estimated_tokens
    elapsed_secs = now - callback_context.state["timer_start"]
    
    logger.debug(
        "rate_limit_callback [timestamp: %i, request_count: %i, token_count: %i, elapsed_secs: %i]",
        now,
        request_count,
        token_count,
        elapsed_secs,
    )
    
    # Enforce rate limits (check both request and token quotas)
    if request_count > RPM_QUOTA or token_count > TPM_QUOTA:
        delay = RATE_LIMIT_SECS - elapsed_secs + 1
        if delay > 0:
            reason = []
            if request_count > RPM_QUOTA:
                reason.append(f"requests: {request_count}/{RPM_QUOTA}")
            if token_count > TPM_QUOTA:
                reason.append(f"tokens: {token_count}/{TPM_QUOTA}")
            
            logger.debug(
                "Sleeping for %i seconds to respect rate limit (%s)",
                delay,
                ", ".join(reason)
            )
            time.sleep(delay)
        
        # Reset timer window
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
        callback_context.state["token_count"] = estimated_tokens
    else:
        callback_context.state["request_count"] = request_count
        callback_context.state["token_count"] = token_count
    
    return
