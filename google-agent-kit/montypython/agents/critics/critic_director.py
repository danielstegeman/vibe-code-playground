"""Consistency critic for Director agent"""

from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from ...config import Config
from ...callbacks import rate_limit_callback


critic_director_agent = Agent(
    model=LiteLlm(
        model=Config.MODEL_NAME,
        timeout=Config.MODEL_TIMEOUT,
        max_retries=Config.MODEL_MAX_RETRIES,
        tpm=Config.TPM
    ),
    name='critic_director_agent',
    description='Evaluates director_delegator_agent adherence to instruction guidelines',
    instruction="""You are a consistency critic evaluating how well the director_delegator_agent followed strategic selection guidelines.

YOUR TASK:
Review the conversation history and analyze the director's performer selection patterns.

Judge each selection decision in isolation - did it match strategic requirements for continuation vs switching, conflict pairing, and archetype matching based on the scene state at that moment?

OUTPUT FORMAT (2 paragraphs maximum):

Paragraph 1: Overall Adherence Grade (X/10) and Degradation Score (X/10). Brief statement of how consistently the director made strategic selections, with specific turn numbers cited as examples of good/poor choices.

Paragraph 2: Key observation about selection patterns - did strategy remain consistent, improve, or degrade over time? One specific example of best selection and one of worst selection.

Be concise and objective. Focus on whether selections aligned with stated director strategy.""",,
    before_model_callback=rate_limit_callback
)
