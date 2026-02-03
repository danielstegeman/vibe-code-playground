"""Main entry point for Monty Python Improv System"""

from google.adk.runners import InMemoryRunner
from agents.director import director_agent, get_single_agent_director
from config import Config


def main():
    """Run the Monty Python improv system"""
    
    # Select agent mode
    if Config.USE_SINGLE_AGENT:
        agent = get_single_agent_director()
        mode = "SINGLE-AGENT MODE"
    else:
        agent = director_agent
        mode = "MULTI-AGENT MODE"
    
    print("=" * 60)
    print("MONTY PYTHON IMPROV THEATRE")
    print("=" * 60)
    print(f"\n[{mode}]")
    print("\nWelcome to the Monty Python Improv System!")
    print("Featuring: John Cleese, Graham Chapman, Terry Jones,")
    print("          Terry Gilliam, Eric Idle, and Michael Palin\n")
    
    runner = InMemoryRunner(
        agent=agent,
        app_name="monty_python_improv"
    )
    
    while True:
        print("-" * 60)
        scene_prompt = input("\nEnter a scene prompt (or 'quit' to exit): ").strip()
        
        if scene_prompt.lower() in ['quit', 'exit', 'q']:
            print("\nThank you for visiting the Monty Python Improv Theatre!")
            print("And now for something completely different...")
            break
        
        if not scene_prompt:
            print("Please provide a scene prompt.")
            continue
        
        print("\n" + "=" * 60)
        print(f"SCENE: {scene_prompt}")
        print("=" * 60 + "\n")
        
        try:
            for event in runner.run(scene_prompt):
                if event.content:
                    print(event.content)
                    print()
        except KeyboardInterrupt:
            print("\n\nScene interrupted!")
            continue
        except Exception as e:
            print(f"\nError during scene: {e}")
            continue
        
        print("\n" + "=" * 60)
        print("SCENE COMPLETE")
        print("=" * 60)


if __name__ == "__main__":
    main()
