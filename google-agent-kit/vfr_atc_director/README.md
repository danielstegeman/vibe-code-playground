# VFR ATC Director Agent

Voice-enabled Visual Flight Rules (VFR) Air Traffic Control simulation using Google Agent Development Kit (ADK) with native Gemini audio-preview models.

## Overview

The VFR ATC Director is an orchestrator agent that coordinates specialist ATC controller sub-agents (Tower, Ground, Clearance, etc.) to provide realistic air traffic control services with proper FAA/ICAO phraseology and procedures.

### Architecture

```
┌─────────────────────────────────────┐
│      VFR ATC Director Agent         │
│    (Root Orchestrator)              │
│  - Routes pilot requests            │
│  - Maintains continuity             │
│  - Handles edge cases               │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┬──────────┬─────────┐
       │                │          │         │
   ┌───▼────┐    ┌─────▼──┐  ┌───▼────┐  ┌─▼────────┐
   │ Tower  │    │ Ground │  │Clearance│  │Approach/ │
   │ Agent  │    │ Agent  │  │ Agent   │  │Departure │
   │(Future)│    │(Future)│  │(Future) │  │ (Future) │
   └────────┘    └────────┘  └─────────┘  └──────────┘
```

**Current Status**: Foundation implemented - Director agent with orchestration logic. Sub-agents to be implemented in subsequent steps.

## Features

- ✅ **Airport-Agnostic**: Works with any airport configuration
- ✅ **Realistic Phraseology**: Enforces proper ATC communication standards
- ✅ **Multi-Agent Architecture**: Director orchestrates specialist controllers
- 🚧 **Bidirectional Audio**: Voice input/output (framework ready, streaming to be completed)
- 🚧 **Specialist Sub-Agents**: Tower, Ground, Clearance, Approach (to be implemented)
- 🚧 **ATC Tools**: Airport data, weather, NOTAM, phraseology validation (to be implemented)

## Requirements

### Software

- Python 3.11 or higher
- Google ADK 1.22.1+
- Google Generative AI SDK 1.59.0+

### API Keys

- Google API Key with access to Gemini models
- (Optional) Google Cloud Project ID for enhanced features

### Audio Dependencies (for voice mode)

```bash
pip install pyaudio sounddevice  # For microphone/speaker I/O
```

## Installation

1. **Clone or navigate to the workspace**:
```bash
cd google-agent-kit/vfr_atc_director
```

2. **Install dependencies** (from google-agent-kit root):
```bash
pip install -r requirements.txt
```

3. **Set environment variables**:
```bash
# Windows (PowerShell)
$env:GOOGLE_API_KEY="your-google-api-key"

# Linux/macOS
export GOOGLE_API_KEY="your-google-api-key"
```

## Configuration

Edit [config.py](config.py) to customize:

### Model Settings
- `MODEL_NAME`: Gemini model (default: `gemini-2.5-flash-native-audio-preview-12-2025`)
- `MODEL_TIMEOUT`: Request timeout in seconds
- `MODEL_MAX_RETRIES`: Retry attempts on failure

### Audio Settings
- `AUDIO_SAMPLE_RATE`: Sample rate in Hz (default: 16000)
- `AUDIO_CHANNELS`: Mono (1) or Stereo (2)
- `AUDIO_FORMAT`: Encoding format (default: LINEAR16)

### Simulation Settings
- `AIRPORT_AGNOSTIC`: Enable airport-agnostic mode (default: True)
- `PHRASEOLOGY_STRICT`: Enforce strict ATC phraseology (default: True)
- `TRAINING_MODE`: Enable educational feedback (default: False)

## Usage

### Text Mode (Current)

Run the director in text mode for testing:

```bash
python -m vfr_atc_director.main
```

**Example interaction**:
```
PILOT: Cessna 1234 Alpha, 10 miles north, inbound for landing
ATC: Cessna 34 Alpha, standby. Specialist controllers are being configured.

PILOT: quit
ATC: Closing frequency. Good day!
```

### Voice Mode (To Be Implemented)

Future audio streaming implementation will enable:
- Voice input from microphone (pilot transmissions)
- Voice output to speakers (ATC responses)
- Real-time bidirectional communication

## Development Status

### ✅ Completed (Step 1)

- [x] Project structure and organization
- [x] Configuration management system
- [x] Director agent with orchestration logic
- [x] Native Gemini SDK integration
- [x] Text-based CLI runner for testing
- [x] Audio streaming framework (skeleton)

### 🚧 In Progress

- [ ] Complete audio streaming implementation
- [ ] Microphone input handling
- [ ] Speaker output handling
- [ ] Test with actual audio devices

### 📋 Planned (Future Steps)

**Step 2: Tower Controller Agent**
- [ ] Pattern work coordination
- [ ] Takeoff/landing clearances
- [ ] Traffic sequencing
- [ ] Go-around procedures

**Step 3: Ground Controller Agent**
- [ ] Taxiway routing
- [ ] Ramp operations
- [ ] Runway crossing clearances
- [ ] Progressive taxi instructions

**Step 4: ATC Phraseology Tools**
- [ ] Phraseology validator
- [ ] Standard terminology enforcer
- [ ] Position report parser
- [ ] Read-back verification

**Step 5: Airport Data Integration**
- [ ] Airport database (runways, taxiways, frequencies)
- [ ] Weather/METAR retrieval
- [ ] NOTAM information
- [ ] Traffic state manager

## Architecture Notes

### Director Pattern

The director agent operates as a **pure orchestrator**:
- Does NOT provide direct ATC services
- Routes requests to appropriate specialist sub-agents
- Maintains conversation continuity
- Handles edge cases and unusual situations

### Native Gemini SDK

This project uses the **native Gemini SDK** (not LiteLLM) for:
- Access to audio-preview models
- Native audio streaming capabilities
- Real-time bidirectional communication
- Multimodal input/output

### Airport-Agnostic Design

The system is designed to work with any airport:
- No hardcoded airport-specific data
- Configurable via tools and sub-agents
- Specialist agents handle airport-specific procedures
- Scalable to multiple airports

## Troubleshooting

### Configuration Errors

```
Configuration Error: GOOGLE_API_KEY environment variable is required
```

**Solution**: Set the `GOOGLE_API_KEY` environment variable:
```bash
export GOOGLE_API_KEY="your-api-key"
```

### Model Access Issues

If you encounter errors about model availability:
1. Verify your API key has access to Gemini models
2. Check model name: `gemini-2.5-flash-native-audio-preview-12-2025`
3. Ensure google-genai package is up to date: `pip install --upgrade google-genai`

### Audio Issues (Future)

For audio streaming problems:
1. Check microphone/speaker permissions
2. Verify audio device availability
3. Enable audio logging: `Config.LOG_AUDIO_STREAMS = True`

## Contributing

When adding new features:
1. Follow existing code structure and patterns
2. Update this README with new capabilities
3. Add appropriate logging
4. Include error handling
5. Document configuration options

## Next Steps

1. **Test Director Agent**: Run in text mode and verify orchestration logic
2. **Implement Tower Agent**: First specialist sub-agent (Step 2)
3. **Complete Audio Streaming**: Finish bidirectional voice I/O
4. **Add ATC Tools**: Airport data, weather, phraseology validation

## License

Part of the vibe-code-playground project.

## Contact

For questions or issues, please refer to the main project documentation.
