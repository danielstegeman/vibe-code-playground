"""Simple test script to verify Claude API connectivity."""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from swarms import Agent

# Load environment variables
load_dotenv()

# Check for API key
if not os.getenv("ANTHROPIC_API_KEY"):
    print("❌ ERROR: ANTHROPIC_API_KEY not found in .env file")
    print("Please add your Anthropic API key to the .env file")
    exit(1)

print("🔗 Testing Claude API connectivity...\n")

# Create a simple agent with Claude
agent = Agent(
    agent_name="Hello-World-Agent",
    system_prompt="You are a friendly assistant. Keep your responses brief and cheerful.",
    model_name="anthropic/claude-sonnet-4-5",
    max_loops=1,
    verbose=True,
    temperature=0.7,
    top_p=None,
)

# Run a simple hello world test
print("📤 Sending test message to Claude...\n")

try:
    response = agent.run("Say hello world and tell me you're working correctly!")
    
    print("\n" + "="*80)
    print("✅ SUCCESS! Claude responded:")
    print("="*80)
    print(f"\n{response}\n")
    print("="*80)
    print("\n🎉 Claude API connectivity confirmed!")
    
except Exception as e:
    print("\n" + "="*80)
    print("❌ ERROR: Failed to connect to Claude")
    print("="*80)
    print(f"Error: {e}")
