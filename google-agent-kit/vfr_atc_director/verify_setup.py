"""Quick verification script for VFR ATC Director Agent setup."""

import sys
import os

print("=" * 70)
print("VFR ATC DIRECTOR - Installation Verification")
print("=" * 70)
print()

# Check Python version
print(f"✓ Python version: {sys.version.split()[0]}")

# Check imports
try:
    from vfr_atc_director.config import Config
    print("✓ Config module imported")
except ImportError as e:
    print(f"✗ Config import failed: {e}")
    sys.exit(1)

try:
    import google.genai as genai
    print("✓ google.genai available")
except ImportError as e:
    print(f"✗ google.genai not available: {e}")
    print("  Install with: pip install google-genai")
    sys.exit(1)

try:
    from google.adk.agents.llm_agent import Agent
    print("✓ Google ADK available")
except ImportError as e:
    print(f"✗ Google ADK not available: {e}")
    print("  Install with: pip install google-adk")
    sys.exit(1)

# Check API key
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    print(f"✓ GOOGLE_API_KEY is set ({len(api_key)} chars)")
else:
    print("⚠ GOOGLE_API_KEY not set (required to run)")
    print("  Set with: export GOOGLE_API_KEY='your-key'")

# Check configuration
print()
print("Configuration:")
print(f"  Model: {Config.MODEL_NAME}")
print(f"  Audio Sample Rate: {Config.AUDIO_SAMPLE_RATE} Hz")
print(f"  Phraseology: {'Strict' if Config.PHRASEOLOGY_STRICT else 'Permissive'}")
print(f"  Airport-Agnostic: {Config.AIRPORT_AGNOSTIC}")

# Try to import agent (will fail without API key)
if api_key:
    print()
    try:
        from vfr_atc_director.agent import root_agent
        print("✓ Director agent initialized successfully")
        print(f"  Agent name: {root_agent.name}")
        print(f"  Sub-agents: {len(root_agent.sub_agents)}")
        print(f"  Tools: {len(root_agent.tools)}")
    except Exception as e:
        print(f"✗ Agent initialization failed: {e}")
        import traceback
        traceback.print_exc()

print()
print("=" * 70)
print("Verification complete!")
if api_key:
    print("Ready to run: python -m vfr_atc_director.main")
else:
    print("Set GOOGLE_API_KEY to run the director agent")
print("=" * 70)
