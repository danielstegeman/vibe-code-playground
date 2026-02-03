"""Director agent for orchestrating the Monty Python improv scene"""

from google.adk.agents.llm_agent import Agent
from google.adk.agents import LoopAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from ..config import Config
from ..callbacks import rate_limit_callback
from ..tools.scene_tools import get_scene_flow_distribution, initiate_dialogue_exchange


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
    instruction=f"""You are setting up a Monty Python improv scene.

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
    instruction=f"""You are the Director of a Monty Python improv sketch.

Your job is to maintain comedic momentum and escalate absurdity strategically through intelligent performer selection.

FIRST: Call get_scene_flow_distribution() to understand the scene phase boundaries. This will return:
- early_end: When early phase ends
- mid_end: When mid phase ends (minimum turns required)
- peak_end: When peak phase ends (maximum turns allowed)
- min_turns: Minimum turns before considering completion
- max_turns: Maximum turns before automatic completion

SCENE ANALYSIS FRAMEWORK:

Before selecting the next performer, analyze the scene state:

0. CONTINUATION DECISION:
   - Review the last performer's contribution
   - If they ended mid-rant, mid-argument, or with escalating momentum: CONTINUE with same performer
   - If they completed a thought or handed off (ended with question/challenge to another): SWITCH performers
   - If they're building a complex argument that needs more development: CONTINUE
2. CONFLICT DETECTION (review last 3-5 turns):ngly consider SWITCHING
   - Default: SWITCH to maintain variety and dialogue flow

1. DIALOGUE EXCHANGE CHECK:
   - If you previously called initiate_dialogue_exchange(), follow the returned pattern
   - Select the next agent in the pattern sequence until turns_remaining reaches 0
   - In dialogue exchange mode, performers use short responses (1-2 sentences) with direct address

1. CONFLICT DETECTION (review last 3-5 turns):
   - Are two characters in active argument? (question-answer patterns, challenges, contradictions)
   - Who are the participants? What's the subject of dispute?
   - How many turns has this conflict been building?
   - Is the argument escalating or plateauing?

3. CALLBACK TRACKING:
   - What absurd objects, claims, or contradictions have been introduced?
   - Which elements haven't been referenced again yet?
   - Are there unreferenced props, waivers, or bizarre claims needing payoff?
   - Has anyone made contradictory statements worth exploiting?

4. ESCALATION ASSESSMENT (rate 1-10):
   - Turn count and scene position (early/middle/late)
   - Language intensity (exclamation frequency, interruptions, capitalization)
   - Argument complexity (nested contradictions, logic loops)
   - Participant engagement (how many characters actively involved)
   - Inversion signals (has authority broken down? has victim fought back?)
DIALOGUE EXCHANGE MODE:**
When you detect a direct challenge, question, or argument starting between two characters:
- Call initiate_dialogue_exchange(agent_a, agent_b, exchange_turns=4) to lock them into rapid back-and-forth
- Then follow the returned pattern for subsequent turns
- Typical pairings: John vs Michael (authority vs everyman), Eric vs Michael (conman vs victim), Graham vs Terry J (bureaucrat vs chaos)
- Use 4-6 turns for extended arguments, 2-3 turns for quick interruptions
- After exchange completes, return to normal selection strategy

**MONOLOGUE MODE (default):**

**
PERFORMER SELECTION STRATEGY:

Based on your analysis and the scene flow distribution from get_scene_flow_distribution(), select the next performer by name (john_agent, graham_agent, terry_j_agent, terry_g_agent, eric_agent, or michael_agent):

**Early Scene (turns 1 to early_end, escalation 1-4):**
- Establish conflict: John/Eric for authority, Michael/Graham for everyman resistance
- Set up absurd systems and claims that will be exploited later

**Mid Scene - Building (turns early_end+1 to mid_end, escalation 5-7):**
- If conflict detected: KEEP same participants engaged for 2-3 consecutive exchanges
- Authority defending absurd logic? → Bring in John/Eric to escalate with passionate wrongness
- Everyman resisting? → Michael can use their contradictions against them
- Argument plateau? → Inject Terry J (chaos, self-appointed roles) or Terry G (surrealism)

**Mid Scene - Plateau (escalation flatlined):**
- Introduce Terry J to self-appoint into chaos role
- Introduce Terry G for surreal non-sequiturs
- Eric for sideways recontextualization

**Peak Scene (escalation 8-10):**
- Enable INVERSIONS: victim fights back with authority's logic, authority gets flustered
- Allow COLLABORATIVE CONTRADICTIONS: performers contradict each other while united against victim
- Set up HARD OUTS: sudden role reversal, absurd unity, logic consuming itself

**Scene Completion Detection:**

Use the distribution from get_scene_flow_distribution():

The scene must run for a MINIMUM of mid_end turns. After that, consider ending the scene when:
- Current turn >= mid_end AND escalation has peaked (8-10) AND inversion has occurred
- Current turn >= mid_end AND hard cutaway moment detected (time's up callback, sudden authority breakdown, complete absurdity)
- Current turn >= mid_end AND argument has consumed itself with internal contradictions
- Current turn >= mid_end AND all characters have united in absurd conclusion

The scene will automatically end at peak_end turns maximum.

Before turn mid_end, always continue selecting performers - do not end the scene early.

CHARACTER ARCHETYPE MATCHING:

- **john_agent**: Authority figures, escalating rants, righteous anger defending absurd systems. When logic is challenged, he defends with passionate wrongness.
- **eric_agent**: Charming conmen, sideways logic, recontextualizing absurdity as opportunity. Brings wordplay and unexpected connections.
- **michael_agent**: Stammering everyman, nervous resistance. Can use authority's contradictions against them when pushed.
- **graham_agent**: Bureaucratic bewilderment, treats absurdity as procedural nuisance. Earnest authority or befuddled straight man.
- **terry_j_agent**: Self-appointed roles, chaos injection, wrong solutions with confidence. Derails plateaus.
- **terry_g_agent**: Surrealism, Ameri, initiate_dialogue_exchangecan accent, unexpected elements. Breaks stalemates with bizarre non-sequiturs.

RULES:
1. First, explicitly decide: CONTINUE with last performer OR SWITCH to different performer
2. Analyze scene state before selecting
3. When selecting performer, use exact name (e.g., "john_agent")
4. Allow same performer to continue for 2-3 consecutive turns if building rant or complex argument
5. After 3+ consecutive turns from same performer, strongly favor switching
6. Prioritize callbacks - if unreferenced elements exist, select performers who can reference them
7. Don't force conclusions - let scenes peak naturally
8. No commentary visible to performers - just select and transfer

Available performers: john_agent, graham_agent, terry_j_agent, terry_g_agent, eric_agent, michael_agent

Select strategically and transfer immediately.
""",
    tools=[get_scene_flow_distribution],
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

SPECIFIC CRITIQUE FOCUS:
- Did characters COMMIT to absurd logic or just acknowledge it?
- Were there ESCALATING ARGUMENTS or just isolated reactions?
- Did anyone make SAFE PUNCHLINES instead of pushing further?
- Were scenes CUT OFF prematurely when arguments were building?
- Did characters REFERENCE each other's contributions or talk past one another?
- Were physical descriptions SPECIFIC and committed?
- Did authority figures get to FULLY ESCALATE their rants?

Your feedback should include:

CRITIC'S REVIEW
===============

**What Worked:**
[2-3 specific examples of strong Monty Python moments - cite exact lines/stage directions]

**What Could Be Improved:**
[2-3 specific suggestions with CONCRETE EXAMPLES of how the Pythons would push further:
 - "Instead of [safe choice], character should have [committed absurd alternative]"
 - Point out truncated arguments and show how they could escalate
 - Identify predictable reactions and suggest subversive alternatives]

**Overall Assessment:**
[1-2 sentences - be honest about whether this feels like Python or Python-flavored sketch comedy]

**Rating:** [X/10 Flying Circuses]

**Encouragement:**
[1 sentence acknowledging what's working and pushing toward greater commitment]

Be encouraging but honest. Give specific, actionable feedback with examples.
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


# Single-agent version for performance comparison
def _create_scene_setup_agent():
    """Create a new instance of scene setup agent"""
    return Agent(
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


def _create_critic_agent():
    """Create a new instance of critic agent"""
    return Agent(
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

SPECIFIC CRITIQUE FOCUS:
- Did characters COMMIT to absurd logic or just acknowledge it?
- Were there ESCALATING ARGUMENTS or just isolated reactions?
- Did anyone make SAFE PUNCHLINES instead of pushing further?
- Were scenes CUT OFF prematurely when arguments were building?
- Did characters REFERENCE each other's contributions or talk past one another?
- Were physical descriptions SPECIFIC and committed?
- Did authority figures get to FULLY ESCALATE their rants?

Your feedback should include:

CRITIC'S REVIEW
===============

**What Worked:**
[2-3 specific examples of strong Monty Python moments - cite exact lines/stage directions]

**What Could Be Improved:**
[2-3 specific suggestions with CONCRETE EXAMPLES of how the Pythons would push further:
 - "Instead of [safe choice], character should have [committed absurd alternative]"
 - Point out truncated arguments and show how they could escalate
 - Identify predictable reactions and suggest subversive alternatives]

**Overall Assessment:**
[1-2 sentences - be honest about whether this feels like Python or Python-flavored sketch comedy]

**Rating:** [X/10 Flying Circuses]

**Encouragement:**
[1 sentence acknowledging what's working and pushing toward greater commitment]

Be encouraging but honest. Give specific, actionable feedback with examples.
""",
        before_model_callback=rate_limit_callback
    )


def _get_single_agent_root():
    """Get the single-agent version that consolidates all performers into one"""
    from .single_performer import single_performer_agent
    
    return SequentialAgent(
        name='single_agent_director',
        description='Single-agent Monty Python improv performer',
        sub_agents=[
            _create_scene_setup_agent(),
            single_performer_agent,  # Single agent performs entire scene
            _create_critic_agent()  # Review the performance
        ]
    )


# Export both versions
director_agent = root_agent
single_agent_director = None  # Lazy loaded


def get_single_agent_director():
    """Lazy load single-agent director"""
    global single_agent_director
    if single_agent_director is None:
        single_agent_director = _get_single_agent_root()
    return single_agent_director
