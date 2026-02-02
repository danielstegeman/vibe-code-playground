"""Director agent for orchestrating the Monty Python improv scene"""

from google.adk.agents.llm_agent import Agent
from google.adk.agents import LoopAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from ..config import Config
from ..callbacks import rate_limit_callback
from ..tools.scene_tools import select_random_performer


# Scene setup agent - runs once at the beginning
scene_setup_agent = Agent(
    model=LiteLlm(
        model=Config.MODEL_NAME,
        timeout=Config.MODEL_TIMEOUT,
        max_retries=Config.MODEL_MAX_RETRIES,
        tpm=Config.TPM
    ),
    name='scene_setup_agent',
    description='Sets up the initial scene based on user prompt',
    instruction="""You are setting up a Monty Python improv scene.

Based on the user's scene prompt, provide a brief (1-2 sentences) scene setup that establishes:
- The setting
- The situation
- Any initial context

Keep it brief and punchy. The performers will take it from here.

Output ONLY the scene setup text.
""",
    output_key='scene_context',
    before_model_callback=rate_limit_callback
)


# Director agent that delegates to performers
director_delegator_agent = Agent(
    model=LiteLlm(
        model=Config.MODEL_NAME,
        timeout=Config.MODEL_TIMEOUT,
        max_retries=Config.MODEL_MAX_RETRIES,
        tpm=Config.TPM
    ),
    name='director_delegator_agent',
    description='Director that selects and delegates to performers',
    instruction="""You are the Director of a Monty Python improv sketch.

Your job is to:
1. Call select_random_performer() to pick the next performer
2. Immediately transfer to that performer agent with brief scene context

Keep the scene moving. No commentary, no narration. Just pick a performer and transfer.

Available performers: john_agent, graham_agent, terry_j_agent, terry_g_agent, eric_agent, michael_agent
""",
    tools=[select_random_performer],
    sub_agents=[],  # Will be configured later
    before_model_callback=rate_limit_callback
)


def _configure_director_sub_agents():
    """Configure performer sub-agents after all agents are loaded"""
    from .john import john_agent
    from .graham import graham_agent
    from .terry_j import terry_j_agent
    from .terry_g import terry_g_agent
    from .eric import eric_agent
    from .michael import michael_agent
    
    director_delegator_agent.sub_agents = [
        john_agent,
        graham_agent,
        terry_j_agent,
        terry_g_agent,
        eric_agent,
        michael_agent
    ]


def _get_performance_loop():
    """Get the performance loop agent"""
    # Configure director's sub-agents
    _configure_director_sub_agents()
    
    # Create the loop that runs the director repeatedly
    return LoopAgent(
        name='performance_loop',
        sub_agents=[director_delegator_agent],
        max_iterations=Config.MAX_TURNS
    )


# Script compilation agent - runs after the performance loop
script_compiler_agent = Agent(
    model=LiteLlm(
        model=Config.MODEL_NAME,
        timeout=Config.MODEL_TIMEOUT,
        max_retries=Config.MODEL_MAX_RETRIES,
        tpm=Config.TPM
    ),
    name='script_compiler_agent',
    description='Compiles the complete scene script',
    instruction="""You are compiling the final script for a Monty Python improv scene.

Review the entire conversation history and create a properly formatted movie script.

Your output should be:

1. First line: "--- END OF SCENE ---"
2. A blank line
3. Then the complete script formatted as:

COMPLETE SCRIPT
===============

[Scene setup text]

[All performer dialogue with character names and stage directions]

THE END

Format each performer's contribution as:
CHARACTER NAME
(stage direction)
Dialogue text.

Maintain chronological order. Include ALL performers' contributions from the scene.
""",
    before_model_callback=rate_limit_callback
)


# Critic agent - reviews the scene for Monty Python authenticity
critic_agent = Agent(
    model=LiteLlm(
        model=Config.MODEL_NAME,
        timeout=Config.MODEL_TIMEOUT,
        max_retries=Config.MODEL_MAX_RETRIES,
        tpm=Config.TPM
    ),
    name='critic_agent',
    description='Reviews the scene for Monty Python style and provides feedback',
    instruction="""You are a Monty Python comedy critic and expert.

Review the script that was just performed and provide constructive feedback.

Evaluate the scene on these Monty Python hallmarks:
- ABSURDISM: Non-sequiturs, surreal elements, escalating ridiculousness
- BRITISH HUMOR: Wordplay, class commentary, dry wit, understatement
- CHARACTER WORK: Distinct voices, physical comedy descriptions, commitment to bit
- STRUCTURE: Building tension, callbacks, subverting expectations
- PYTHONESQUE ELEMENTS: Authority figures undermined, pedantic arguments, sudden left turns

Your feedback should include:

CRITIC'S REVIEW
===============

**What Worked:**
[2-3 specific examples of strong Monty Python moments]

**What Could Be Improved:**
[2-3 specific suggestions for being more Pythonesque]

**Overall Assessment:**
[1-2 sentences summarizing how well this captured the Monty Python spirit]

**Rating:** [X/10 Flying Circuses]

Be encouraging but honest. Give specific, actionable feedback.
""",
    before_model_callback=rate_limit_callback
)


# The root agent combines setup + loop + compilation + critique
root_agent = SequentialAgent(
    name='director_agent',
    description='Monty Python improv director using loop-based performance',
    sub_agents=[
        scene_setup_agent,
        _get_performance_loop(),
        script_compiler_agent,  # Compile script after performance ends
        critic_agent  # Review the performance
    ]
)
