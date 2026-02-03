"""Critic aggregator that summarizes all consistency reports"""

from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from ...config import Config
from ...callbacks import rate_limit_callback


critic_aggregator_agent = Agent(
    model=LiteLlm(
        model=Config.MODEL_NAME,
        timeout=Config.MODEL_TIMEOUT,
        max_retries=Config.MODEL_MAX_RETRIES,
        tpm=Config.TPM
    ),
    name='critic_aggregator_agent',
    description='Aggregates all critic reports into a summary',
    instruction="""You are aggregating consistency reports from all critic agents.

Review the previous 7 agent outputs and extract the Overall Adherence Grade and Degradation Score from each.

OUTPUT FORMAT (table only, 3 lines maximum):

| Agent          | Adherence | Degradation | Avg |
|----------------|-----------|-------------|-----|
| John Cleese    | X/10      | X/10        | X.X |
| Eric Idle      | X/10      | X/10        | X.X |
| Michael Palin  | X/10      | X/10        | X.X |
| Graham Chapman | X/10      | X/10        | X.X |
| Terry Jones    | X/10      | X/10        | X.X |
| Terry Gilliam  | X/10      | X/10        | X.X |
| Director       | X/10      | X/10        | X.X |
| **SYSTEM AVG** | **X.X**   | **X.X**     | **X.X** |

Line 2: Best performer: [Agent] (X/10 adherence). Worst degradation: [Agent] (X/10).

Line 3: One-sentence overall assessment of system consistency.
""",
    before_model_callback=rate_limit_callback
)
