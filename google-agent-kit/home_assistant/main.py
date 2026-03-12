"""CLI entry point for the Home Assistant multi-agent system."""

import asyncio

from google.adk.runners import InMemoryRunner
from google.genai import types

from .agent import root_agent
from .config import Config
from .state.store import reset_state


async def run_prompt(prompt: str) -> str:
    """Send *prompt* through the orchestrator and return the final text reply."""
    reset_state()
    runner = InMemoryRunner(agent=root_agent, app_name=Config.APP_NAME)
    session = await runner.session_service.create_session(
        app_name=Config.APP_NAME, user_id=Config.USER_ID
    )

    content = types.Content(
        role="user", parts=[types.Part.from_text(text=prompt)]
    )

    reply_parts: list[str] = []
    async for event in runner.run_async(
        user_id=Config.USER_ID, session_id=session.id, new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    reply_parts.append(part.text)

    return "\n".join(reply_parts)


async def interactive() -> None:
    """Run an interactive console session."""
    reset_state()
    runner = InMemoryRunner(agent=root_agent, app_name=Config.APP_NAME)
    session = await runner.session_service.create_session(
        app_name=Config.APP_NAME, user_id=Config.USER_ID
    )

    print("Home Assistant (type 'quit' to exit)")
    print("-" * 40)

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input or user_input.lower() in ("quit", "exit"):
            break

        content = types.Content(
            role="user", parts=[types.Part.from_text(text=user_input)]
        )

        async for event in runner.run_async(
            user_id=Config.USER_ID,
            session_id=session.id,
            new_message=content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
        print()


def main() -> None:
    """Entry point."""
    asyncio.run(interactive())


if __name__ == "__main__":
    main()
