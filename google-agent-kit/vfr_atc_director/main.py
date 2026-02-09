"""Main entry point for VFR ATC Director Agent with multiple input modes.

Supports:
- Text mode: CLI interaction (python -m vfr_atc_director.main)
- Audio mode: Microphone streaming (python -m vfr_atc_director.main --mode audio)
- Web mode: Web interface with voice (adk web)
"""

import sys
import logging
import argparse
import asyncio
from google.adk.runners import InMemoryRunner

from .config import Config
from .agent import root_agent


# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_with_audio():
    """Run with microphone audio streaming.
    
    References:
    - https://google.github.io/adk-docs/streaming/dev-guide/part2/#sending-audio
    - https://google.github.io/adk-docs/streaming/dev-guide/part5/#sending-audio-input
    - https://github.com/google/adk-samples/tree/main/python/agents/bidi-demo
    """
    try:
        import pyaudio
    except ImportError:
        print("\n❌ PyAudio not installed!")
        print("\nInstall with: pip install pyaudio")
        print("\nAlternatively, use web mode: adk web --port 8000")
        return
    
    from google.genai import types
    from google.adk.agents.run_config import RunConfig, StreamingMode
    from google.adk.agents.live_request_queue import LiveRequestQueue
    
    # Audio configuration matching ADK requirements
    # Reference: Part 5 - Audio Format Requirements
    # https://google.github.io/adk-docs/streaming/dev-guide/part5/#sending-audio-input
    INPUT_FORMAT = pyaudio.paInt16  # 16-bit PCM
    INPUT_CHANNELS = 1              # Mono
    INPUT_RATE = 16000              # 16kHz (required for input)
    INPUT_CHUNK = 1600              # 100ms chunks (16000 * 0.1)
    
    OUTPUT_FORMAT = pyaudio.paInt16 # 16-bit PCM
    OUTPUT_CHANNELS = 1             # Mono
    OUTPUT_RATE = 24000             # 24kHz (model output is higher quality!)
    
    print("=" * 70)
    print("VFR ATC DIRECTOR - Microphone Streaming Mode")
    print("=" * 70)
    print()
    print(f"Model: {Config.MODEL_NAME}")
    print(f"Audio Input: 16-bit PCM, 16kHz, mono")
    print(f"Audio Output: 16-bit PCM, 24kHz, mono")
    print()
    print("🎤 Initializing microphone...")
    print("🔊 Initializing speakers...")
    print()
    
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    
    # Initialize LiveRequestQueue
    # Reference: Part 2 - LiveRequestQueue
    # https://google.github.io/adk-docs/streaming/dev-guide/part2/
    live_request_queue = LiveRequestQueue()
    
    # Configure for audio streaming
    # Reference: Part 4 - RunConfig
    # https://google.github.io/adk-docs/streaming/dev-guide/part4/
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        response_modalities=["AUDIO"],  # Get audio responses
        
        # Audio transcription enabled by default
        # Provides text fallback and captions
        # Reference: Part 5 - Audio Transcription
        # https://google.github.io/adk-docs/streaming/dev-guide/part5/#audio-transcription
    )
    
    try:
        # Open microphone stream
        input_stream = p.open(
            format=INPUT_FORMAT,
            channels=INPUT_CHANNELS,
            rate=INPUT_RATE,
            input=True,
            frames_per_buffer=INPUT_CHUNK,
            stream_callback=None  # Use blocking read
        )
        
        # Open speaker stream
        output_stream = p.open(
            format=OUTPUT_FORMAT,
            channels=OUTPUT_CHANNELS,
            rate=OUTPUT_RATE,
            output=True
        )
        
        print("✅ Microphone active")
        print("✅ Speakers active")
        print()
        print("📻 Frequency open. Speak into microphone to transmit.")
        print("   Press Ctrl+C to close frequency")
        print("-" * 70)
        print()
        
        # Initialize runner
        runner = InMemoryRunner(
            agent=root_agent,
            app_name="vfr_atc_director"
        )
        
        # Create a session for this audio stream
        # Reference: realtime-conversational-agent/server/main.py
        user_id = "pilot_001"
        session = await runner.session_service.create_session(
            app_name="vfr_atc_director",
            user_id=user_id
        )
        
        # Flag to control streaming
        running = True
        
        async def send_audio_loop():
            """Capture microphone audio and send to model.
            
            Reference: Part 2 - Sending Audio
            https://google.github.io/adk-docs/streaming/dev-guide/part2/#sending-audio
            
            Best Practices from Part 5:
            - Send in small chunks for low latency (50-100ms)
            - Don't wait for responses before sending next chunk
            - Model processes audio continuously
            """
            nonlocal running
            while running:
                try:
                    # Read audio chunk from microphone
                    audio_data = input_stream.read(
                        INPUT_CHUNK,
                        exception_on_overflow=False
                    )
                    
                    # Create Blob with proper MIME type
                    # Reference: bidi-demo main.py:181-184
                    audio_blob = types.Blob(
                        mime_type="audio/pcm;rate=16000",
                        data=audio_data
                    )
                    
                    # Send to model
                    # Reference: Part 2 - send_realtime()
                    live_request_queue.send_realtime(audio_blob)
                    
                    # Small async sleep to yield control
                    await asyncio.sleep(0.01)
                    
                except Exception as e:
                    if running:
                        logger.error(f"Error reading microphone: {e}")
                    break
        
        async def receive_events_loop():
            """Receive events from model (audio, text, transcriptions).
            
            Reference: Part 3 - Event Handling
            https://google.github.io/adk-docs/streaming/dev-guide/part3/
            """
            nonlocal running
            try:
                async for event in runner.run_live(
                    session=session,
                    live_request_queue=live_request_queue,
                    run_config=run_config
                ):
                    # Handle content (audio/text responses)
                    # Reference: Part 3 - The Event Class
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            # Audio output from model
                            # Reference: Part 5 - Receiving Audio Output
                            if part.inline_data and part.inline_data.mime_type.startswith("audio/pcm"):
                                # Model outputs 24kHz audio (higher than 16kHz input!)
                                audio_bytes = part.inline_data.data
                                
                                # Play to speakers
                                output_stream.write(audio_bytes)
                            
                            # Text output (fallback or parallel)
                            if part.text:
                                print(f"ATC (text): {part.text}")
                    
                    # Handle input transcription (your speech → text)
                    # Reference: Part 5 - Audio Transcription
                    # Best Practice: Use two-level null checking
                    if event.input_transcription:
                        text = event.input_transcription.text
                        finished = event.input_transcription.finished
                        
                        if text and text.strip():
                            status = "✓" if finished else "..."
                            print(f"PILOT [{status}]: {text}")
                    
                    # Handle output transcription (ATC speech → text)
                    if event.output_transcription:
                        text = event.output_transcription.text
                        finished = event.output_transcription.finished
                        
                        if text and text.strip():
                            status = "✓" if finished else "..."
                            print(f"ATC [{status}]: {text}")
            
            except Exception as e:
                if running:
                    logger.error(f"Error in event loop: {e}")
                    print(f"\n❌ Streaming error: {e}")
        
        # Run send and receive concurrently
        # Reference: Concurrent pattern from bidi-demo
        # https://github.com/google/adk-samples/blob/main/python/agents/bidi-demo/app/main.py#L210-L247
        try:
            await asyncio.gather(
                send_audio_loop(),
                receive_events_loop()
            )
        except KeyboardInterrupt:
            print("\n\n👋 Closing frequency. Good day!")
        finally:
            running = False
            
    finally:
        # Cleanup
        logger.info("Cleaning up audio resources")
        live_request_queue.close()
        
        if 'input_stream' in locals():
            input_stream.stop_stream()
            input_stream.close()
        
        if 'output_stream' in locals():
            output_stream.stop_stream()
            output_stream.close()
        
        p.terminate()


def run_console_mode():
    """Run in console text mode with keyboard input."""
    print("=" * 70)
    print("VFR ATC DIRECTOR - Console Text Mode")
    print("=" * 70)
    print()
    print("💡 TIP: For voice interaction, use:")
    print("   - Microphone: python -m vfr_atc_director.main --mode audio")
    print("   - Web Browser: adk web --port 8000")
    print()
    print(f"Model: {Config.MODEL_NAME}")
    print(f"Airport-Agnostic Mode: {'Enabled' if Config.AIRPORT_AGNOSTIC else 'Disabled'}")
    print(f"Phraseology: {'Strict' if Config.PHRASEOLOGY_STRICT else 'Permissive'}")
    print(f"Training Mode: {'Enabled' if Config.TRAINING_MODE else 'Disabled'}")
    print()
    print("📝 TEXT MODE - Type your messages below")
    print("   Commands: 'quit', 'exit', 'help'")
    print("-" * 70)
    print()
    
    # Initialize ADK runner
    runner = InMemoryRunner(
        agent=root_agent,
        app_name="vfr_atc_director"
    )
    
    print("📻 Frequency open. You are cleared to transmit.")
    print()
    
    while True:
        try:
            # Get user input
            user_input = input("PILOT: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Closing frequency. Good day!")
                break
            
            if user_input.lower() == 'help':
                print("\n📖 HELP:")
                print("  - Type your pilot transmission and press Enter")
                print("  - Use standard aviation phraseology for realistic responses")
                print("  - Commands: quit, exit, help")
                print("  - For voice mode:")
                print("    - Microphone: python -m vfr_atc_director.main --mode audio")
                print("    - Web: adk web --port 8000")
                print()
                continue
            
            # Run agent and stream response
            print("ATC: ", end="", flush=True)
            response_text = ""
            for event in runner.run(user_input):
                if event.content:
                    print(event.content, end="", flush=True)
                    response_text += event.content
            print()
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Closing frequency. Good day!")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            print(f"\n❌ Error: {e}\n")


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description='VFR ATC Director - Multi-modal Air Traffic Control Simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Input Modes:
  Console Text Mode (default):
    python -m vfr_atc_director.main
    
  Voice Mode (Web Interface):
    adk web --port 8000
    - Supports bidirectional audio streaming
    - Automatic voice activity detection
    - Real-time audio transcription
    
  CLI Mode (ADK):
    adk run vfr_atc_director
    - Standard ADK CLI interface
    - Text-based interaction
    
Examples:
  # Run console text mode
  python -m vfr_atc_director.main
  
  # Run with microphone streaming
  python -m vfr_atc_director.main --mode audio
  
  # Show configuration
  python -m vfr_atc_director.main --mode info
  
  # Run with web interface for browser-based voice
  adk web --port 8000
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['console', 'audio', 'info'],
        default='console',
        help='Run mode: console (text CLI), audio (microphone streaming), or info (show configuration)'
    )
    
    args = parser.parse_args()
    
    # Validate configuration
    try:
        Config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease set required environment variables and try again.")
        sys.exit(1)
    
    if args.mode == 'info':
        # Show configuration information
        print("=" * 70)
        print("VFR ATC DIRECTOR - Configuration")
        print("=" * 70)
        print()
        print(f"Model: {Config.MODEL_NAME}")
        print(f"Timeout: {Config.MODEL_TIMEOUT}s")
        print(f"Max Retries: {Config.MODEL_MAX_RETRIES}")
        print()
        print(f"Audio Sample Rate: {Config.AUDIO_SAMPLE_RATE} Hz")
        print(f"Audio Format: {Config.AUDIO_FORMAT}")
        print()
        print(f"Airport-Agnostic: {'Yes' if Config.AIRPORT_AGNOSTIC else 'No'}")
        print(f"Phraseology: {'Strict' if Config.PHRASEOLOGY_STRICT else 'Permissive'}")
        print(f"Training Mode: {'Enabled' if Config.TRAINING_MODE else 'Disabled'}")
        print()
        print("Available Input Modes:")
        print("  1. Console Text: python -m vfr_atc_director.main")
        print("  2. Audio Stream: python -m vfr_atc_director.main --mode audio")
        print("  3. Web Audio: adk web --port 8000")
        print("  4. ADK CLI: adk run vfr_atc_director")
        print()
        print("References:")
        print("  - ADK Streaming Docs: https://google.github.io/adk-docs/streaming/")
        print("  - Audio Guide: https://google.github.io/adk-docs/streaming/dev-guide/part5/")
        print("=" * 70)
    elif args.mode == 'audio':
        # Run audio streaming mode
        asyncio.run(run_with_audio())
    else:
        # Run console mode
        run_console_mode()


if __name__ == "__main__":
    main()