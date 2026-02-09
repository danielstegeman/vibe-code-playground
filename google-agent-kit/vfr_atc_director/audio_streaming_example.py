"""Example: Audio streaming to VFR ATC Director outside web interface.

References:
- https://google.github.io/adk-docs/streaming/dev-guide/part2/#sending-audio
- https://google.github.io/adk-docs/streaming/dev-guide/part5/#sending-audio-input
- https://github.com/google/adk-samples/tree/main/python/agents/bidi-demo
"""

import asyncio
from google.genai import types
from google.adk.runners import InMemoryRunner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.agents.live_request_queue import LiveRequestQueue

from .agent import root_agent


async def stream_audio_example():
    """Example of streaming audio to the agent.
    
    Reference: ADK Bidi-streaming Demo
    https://github.com/google/adk-samples/blob/main/python/agents/bidi-demo/app/main.py#L181-L184
    """
    
    # 1. Create LiveRequestQueue for sending audio
    # Reference: Part 2 - LiveRequestQueue
    # https://google.github.io/adk-docs/streaming/dev-guide/part2/
    live_request_queue = LiveRequestQueue()
    
    # 2. Configure RunConfig for audio streaming
    # Reference: Part 4 - RunConfig
    # https://google.github.io/adk-docs/streaming/dev-guide/part4/
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,  # Bidirectional streaming
        response_modalities=["AUDIO"],       # Model returns audio output
        # input_audio_transcription defaults to enabled
        # output_audio_transcription defaults to enabled
    )
    
    # 3. Initialize runner
    runner = InMemoryRunner(
        agent=root_agent,
        app_name="vfr_atc_director"
    )
    
    # 4. Simulate audio input (in real implementation, read from microphone)
    # Audio format: 16-bit PCM, 16kHz, mono
    # Reference: Part 5 - Audio Format Requirements
    # https://google.github.io/adk-docs/streaming/dev-guide/part5/#sending-audio-input
    
    async def send_audio_chunks():
        """Send audio chunks to the model."""
        # In real implementation, capture from microphone
        # Example: using pyaudio, sounddevice, or browser WebRTC
        
        # Simulated audio data (replace with real audio capture)
        for i in range(10):
            # Read audio chunk from your audio source
            audio_data = get_audio_chunk_from_mic()  # Your implementation
            
            # Create Blob with proper MIME type
            # Reference: main.py:181-184
            audio_blob = types.Blob(
                mime_type="audio/pcm;rate=16000",  # Required format
                data=audio_data                     # Raw bytes (16-bit PCM)
            )
            
            # Send to model using LiveRequestQueue
            # Reference: Part 2 - Sending Audio
            # https://google.github.io/adk-docs/streaming/dev-guide/part2/#sending-audio
            live_request_queue.send_realtime(audio_blob)
            
            # Send audio in small chunks for low latency
            # Recommended: 50-100ms chunks (~1600-3200 bytes @ 16kHz)
            await asyncio.sleep(0.1)  # 100ms chunks
        
        # Signal end of audio input (optional)
        # live_request_queue.send_activity_end()
    
    async def receive_events():
        """Receive audio and text responses from model."""
        # Reference: Part 3 - Event Handling
        # https://google.github.io/adk-docs/streaming/dev-guide/part3/
        
        async for event in runner.run_live(
            user_id="pilot_001",
            session_id="session_001",
            live_request_queue=live_request_queue,
            run_config=run_config
        ):
            # Handle text content
            if event.content and event.content.parts:
                for part in event.content.parts:
                    # Text response
                    if part.text:
                        print(f"ATC (text): {part.text}")
                    
                    # Audio response
                    # Reference: Part 5 - Receiving Audio Output
                    # https://google.github.io/adk-docs/streaming/dev-guide/part5/#receiving-audio-output
                    if part.inline_data and part.inline_data.mime_type.startswith("audio/pcm"):
                        # Audio format: 16-bit PCM, 24kHz, mono
                        audio_bytes = part.inline_data.data
                        
                        # Play audio to speakers (your implementation)
                        play_audio_to_speakers(audio_bytes)
            
            # Handle input transcription (pilot's speech → text)
            # Reference: Part 5 - Audio Transcription
            # https://google.github.io/adk-docs/streaming/dev-guide/part5/#audio-transcription
            if event.input_transcription:
                text = event.input_transcription.text
                finished = event.input_transcription.finished
                if text:
                    print(f"Pilot said: {text} {'[FINAL]' if finished else '[PARTIAL]'}")
            
            # Handle output transcription (ATC's speech → text)
            if event.output_transcription:
                text = event.output_transcription.text
                finished = event.output_transcription.finished
                if text:
                    print(f"ATC said: {text} {'[FINAL]' if finished else '[PARTIAL]'}")
    
    # 5. Run both send and receive concurrently
    # Reference: Bidi-Demo concurrent pattern
    # https://github.com/google/adk-samples/blob/main/python/agents/bidi-demo/app/main.py#L210-L247
    await asyncio.gather(
        send_audio_chunks(),
        receive_events()
    )


def get_audio_chunk_from_mic() -> bytes:
    """Capture audio chunk from microphone.
    
    Audio must be:
    - 16-bit PCM format (signed integer)
    - 16kHz sample rate
    - Mono (single channel)
    
    Example using pyaudio:
        import pyaudio
        
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,  # 16-bit
            channels=1,              # Mono
            rate=16000,              # 16kHz
            input=True,
            frames_per_buffer=1600   # 100ms @ 16kHz
        )
        audio_data = stream.read(1600)
        return audio_data
    
    Example using sounddevice:
        import sounddevice as sd
        import numpy as np
        
        audio = sd.rec(
            frames=1600,      # 100ms @ 16kHz
            samplerate=16000,
            channels=1,
            dtype='int16'
        )
        sd.wait()
        return audio.tobytes()
    """
    # Placeholder - implement your audio capture
    return b'\x00' * 3200  # 100ms silence @ 16kHz (placeholder)


def play_audio_to_speakers(audio_bytes: bytes):
    """Play audio response to speakers.
    
    Audio format from model:
    - 16-bit PCM format
    - 24kHz sample rate (output is higher quality than input!)
    - Mono (single channel)
    
    Reference: Part 5 - Receiving Audio Output
    https://google.github.io/adk-docs/streaming/dev-guide/part5/#receiving-audio-output
    
    Example using pyaudio:
        import pyaudio
        
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,  # 16-bit
            channels=1,              # Mono
            rate=24000,              # 24kHz (output rate!)
            output=True
        )
        stream.write(audio_bytes)
    
    Example using sounddevice:
        import sounddevice as sd
        import numpy as np
        
        audio_array = np.frombuffer(audio_bytes, dtype='int16')
        sd.play(audio_array, samplerate=24000)
        sd.wait()
    """
    # Placeholder - implement your audio playback
    print(f"[Playing {len(audio_bytes)} bytes of audio @ 24kHz]")


# Run the example
if __name__ == "__main__":
    asyncio.run(stream_audio_example())
