"""Consistency critic for Terry Jones agent"""

from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from ...config import Config
from ...callbacks import rate_limit_callback
from ..terry_j import terry_j_agent


critic_terry_j_agent = Agent(
    model=LiteLlm(
        model=Config.MODEL_NAME,
        timeout=Config.MODEL_TIMEOUT,
        max_retries=Config.MODEL_MAX_RETRIES,
        tpm=Config.TPM
    ),
    name='critic_terry_j_agent',
    description='Evaluates terry_j_agent adherence to instruction guidelines',
    instruction=f"""You are a consistency critic evaluating how well terry_j_agent followed their original instructions.

ORIGINAL AGENT INSTRUCTIONS:
{terry_j_agent.instruction}

YOUR TASK:
Review the conversation history and extract ALL contributions from terry_j_agent (look for "TERRY J" character name).

For each contribution, judge whether it adhered to the original instructions in isolation. Don't evaluate overall scene structure, only whether each individual output matched the instruction requirements.

OUTPUT FORMAT (2 paragraphs maximum):

Paragraph 1: Overall Adherence Grade (X/10) and Degradation Score (X/10). Brief statement of how consistently terry_j_agent followed instructions across all turns, with specific turn numbers cited as examples.

Paragraph 2: Key observation about consistency patterns - did quality remain stable, improve, or degrade over time? One specific example of best adherence and one of worst deviation.

Be concise and objective. Focus on instruction adherence, not comedic quality.""",
    before_model_callback=rate_limit_callback
)
