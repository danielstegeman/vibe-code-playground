"""Real-world example: Microphone audio streaming to VFR ATC Director.

This demonstrates a complete implementation using pyaudio for microphone capture
and speaker output.

Install dependencies:
    pip install pyaudio

References:
- ADK Bidi-streaming Demo: https://github.com/google/adk-samples/tree/main/python/agents/bidi-demo
- Part 5 Audio Guide: https://google.github.io/adk-docs/streaming/dev-guide/part5/
"""

import asyncio
import pyaudio
from google.genai import types
from google.adk.runners import InMemoryRunner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.agents.live_request_queue import LiveRequestQueue

from .agent import root_agent
from .config import Config


# Audio configuration matching ADK requirements
INPUT_FORMAT = pyaudio.paInt16  # 16-bit PCM
INPUT_CHANNELS = 1              # Mono
INPUT_RATE = 16000              # 16kHz (required for input)
INPUT_CHUNK = 1600              # 100ms chunks (16000 * 0.1)

OUTPUT_FORMAT = pyaudio.paInt16 # 16-bit PCM
OUTPUT_CHANNELS = 1             # Mono
OUTPUT_RATE = 24000             # 24kHz (model output is higher quality!)


class MicrophoneStreamer:
    """Stream microphone audio to VFR ATC Director agent.
    
    Reference architecture from:
    https://github.com/google/adk-samples/blob/main/python/agents/bidi-demo/app/main.py
    """
    
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.live_request_queue = None
        self.input_stream = None
        self.output_stream = None
        self.running = False
        
    async def start_streaming(self):
        """Start bidirectional audio streaming.
        
        Reference: Part 2 - Sending Messages
        https://google.github.io/adk-docs/streaming/dev-guide/part2/
        """
        print("=" * 70)
        print("VFR ATC DIRECTOR - Voice Streaming Mode")
        print("=" * 70)
        print()
        print("🎤 Microphone: Starting...")
        print("🔊 Speakers: Starting...")
        print()
        
        # Initialize LiveRequestQueue
        # Reference: Part 2 - LiveRequestQueue
        self.live_request_queue = LiveRequestQueue()
        
        # Configure for audio streaming
        # Reference: Part 4 - RunConfig
        # https://google.github.io/adk-docs/streaming/dev-guide/part4/
        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            response_modalities=["AUDIO"],  # Get audio responses
            
            # Audio transcription enabled by default
            # Provides text fallback and captions
            # See: Part 5 - Audio Transcription
            # https://google.github.io/adk-docs/streaming/dev-guide/part5/#audio-transcription
        )
        
        # Open microphone stream
        # Reference: Part 5 - Audio Format Requirements
        # https://google.github.io/adk-docs/streaming/dev-guide/part5/#sending-audio-input
        self.input_stream = self.p.open(
            format=INPUT_FORMAT,
            channels=INPUT_CHANNELS,
            rate=INPUT_RATE,
            input=True,
            frames_per_buffer=INPUT_CHUNK,
            stream_callback=None  # Use blocking read
        )
        
        # Open speaker stream
        # Reference: Part 5 - Receiving Audio Output
        # https://google.github.io/adk-docs/streaming/dev-guide/part5/#receiving-audio-output
        self.output_stream = self.p.open(
            format=OUTPUT_FORMAT,
            channels=OUTPUT_CHANNELS,
            rate=OUTPUT_RATE,
            output=True
        )
        
        print("✅ Microphone active (16kHz, 16-bit PCM, mono)")
        print("✅ Speakers active (24kHz, 16-bit PCM, mono)")
        print()
        print("📻 Frequency open. Speak into microphone to transmit.")
        print("   Press Ctrl+C to close frequency")
        print("-" * 70)
        print()
        
        self.running = True
        
        # Initialize runner
        runner = InMemoryRunner(
            agent=root_agent,
            app_name="vfr_atc_director"
        )
        
        # Run send and receive concurrently
        # Reference: Concurrent pattern from bidi-demo
        # https://github.com/google/adk-samples/blob/main/python/agents/bidi-demo/app/main.py#L210-L247
        try:
            await asyncio.gather(
                self._send_audio_loop(),
                self._receive_events_loop(runner, run_config)
            )
        except KeyboardInterrupt:
            print("\n\n👋 Closing frequency. Good day!")
        finally:
            self.stop()
    
    async def _send_audio_loop(self):
        """Capture microphone audio and send to model.
        
        Reference: Part 2 - Sending Audio
        https://google.github.io/adk-docs/streaming/dev-guide/part2/#sending-audio
        
        Best Practices from Part 5:
        - Send in small chunks for low latency (50-100ms)
        - Don't wait for responses before sending next chunk
        - Model processes audio continuously
        https://google.github.io/adk-docs/streaming/dev-guide/part5/#best-practices-for-sending-audio-input
        """
        while self.running:
            try:
                # Read audio chunk from microphone
                # Blocking read with timeout to allow checking self.running
                audio_data = self.input_stream.read(
                    INPUT_CHUNK,
                    exception_on_overflow=False
                )
                
                # Create Blob with proper MIME type
                # Reference: main.py:181-184 from bidi-demo
                audio_blob = types.Blob(
                    mime_type="audio/pcm;rate=16000",
                    data=audio_data
                )
                
                # Send to model
                # Reference: Part 2 - send_realtime()
                self.live_request_queue.send_realtime(audio_blob)
                
                # Small async sleep to yield control
                await asyncio.sleep(0.01)
                
            except Exception as e:
                if self.running:
                    print(f"❌ Error reading microphone: {e}")
                break
    
    async def _receive_events_loop(self, runner, run_config):
        """Receive events from model (audio, text, transcriptions).
        
        Reference: Part 3 - Event Handling
        https://google.github.io/adk-docs/streaming/dev-guide/part3/
        """
        async for event in runner.run_live(
            user_id="pilot_001",
            session_id="vfr_session_001",
            live_request_queue=self.live_request_queue,
            run_config=run_config
        ):
            # Handle content (audio/text responses)
            # Reference: Part 3 - The Event Class
            # https://google.github.io/adk-docs/streaming/dev-guide/part3/#the-event-class
            if event.content and event.content.parts:
                for part in event.content.parts:
                    # Audio output from model
                    # Reference: Part 5 - Receiving Audio Output
                    if part.inline_data and part.inline_data.mime_type.startswith("audio/pcm"):
                        # Model outputs 24kHz audio (higher than 16kHz input!)
                        audio_bytes = part.inline_data.data
                        
                        # Play to speakers
                        self.output_stream.write(audio_bytes)
                    
                    # Text output (fallback or parallel)
                    if part.text:
                        print(f"ATC (text): {part.text}")
            
            # Handle input transcription (your speech → text)
            # Reference: Part 5 - Audio Transcription
            # https://google.github.io/adk-docs/streaming/dev-guide/part5/#audio-transcription
            if event.input_transcription:
                text = event.input_transcription.text
                finished = event.input_transcription.finished
                
                # Use two-level null checking (best practice)
                # Reference: Part 5 - Best Practice for Transcription Null Checking
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
    
    def stop(self):
        """Stop streaming and cleanup resources."""
        self.running = False
        
        if self.live_request_queue:
            self.live_request_queue.close()
        
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
        
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
        
        self.p.terminate()


async def main():
    """Main entry point for microphone streaming mode."""
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease set required environment variables and try again.")
        return
    
    # Start streaming
    streamer = MicrophoneStreamer()
    await streamer.start_streaming()


if __name__ == "__main__":
    asyncio.run(main())
