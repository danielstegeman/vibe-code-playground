"""ICAO/EASA Standard ATC Phraseology Rules.

This module defines the standard phraseology patterns that ATC controllers
must use for safety-critical communications. Based on ICAO Doc 9432 and
EASA regulations.
"""


class PhraseologyRules:
    """Standard ATC phraseology rules and patterns."""
    
    # Standard clearance phrases
    CLEARANCES = {
        "CLEARED FOR TAKEOFF": ["cleared for takeoff", "cleared to take off"],
        "CLEARED TO LAND": ["cleared to land", "cleared for landing"],
        "LINE UP AND WAIT": ["line up and wait", "line up runway"],
        "HOLD SHORT": ["hold short", "hold position"],
        "TAXI VIA": ["taxi via", "taxi to"],
        "BACKTRACK": ["backtrack", "back track"],
    }
    
    # Avoid informal phrases - these should be replaced with standard alternatives
    INFORMAL_TO_STANDARD = {
        # Informal -> Standard
        "you can land": "cleared to land",
        "you're good to land": "cleared to land",
        "go ahead and land": "cleared to land",
        "you can take off": "cleared for takeoff",
        "you're good to go": "cleared for takeoff",
        "go ahead and take off": "cleared for takeoff",
        "okay to taxi": "taxi via",
        "you can taxi": "taxi via",
        "go ahead": "proceed",
        "wait there": "hold position",
        "stop": "hold position",
        "turn around": "backtrack",
        "go back": "backtrack",
    }
    
    # Phonetic alphabet (ICAO standard)
    PHONETIC_ALPHABET = {
        'A': 'Alpha', 'B': 'Bravo', 'C': 'Charlie', 'D': 'Delta',
        'E': 'Echo', 'F': 'Foxtrot', 'G': 'Golf', 'H': 'Hotel',
        'I': 'India', 'J': 'Juliet', 'K': 'Kilo', 'L': 'Lima',
        'M': 'Mike', 'N': 'November', 'O': 'Oscar', 'P': 'Papa',
        'Q': 'Quebec', 'R': 'Romeo', 'S': 'Sierra', 'T': 'Tango',
        'U': 'Uniform', 'V': 'Victor', 'W': 'Whiskey', 'X': 'X-ray',
        'Y': 'Yankee', 'Z': 'Zulu'
    }
    
    # Number pronunciation (ICAO standard)
    NUMBER_PRONUNCIATION = {
        '0': 'zero',
        '1': 'wun',
        '2': 'too',
        '3': 'tree',
        '4': 'fower',
        '5': 'fife',
        '6': 'six',
        '7': 'seven',
        '8': 'ait',
        '9': 'niner',
    }
    
    # Hundred/thousand rules
    ALTITUDE_RULES = """
Altitudes and flight levels:
- Below 10,000 ft: individual digits (e.g., "niner thousand five hundred")
- 10,000 and above: thousands (e.g., "flight level one hundred")
- QNH: hectopascals (hPa) - e.g., "QNH 1013"
    """
    
    # Standard response format
    RESPONSE_FORMAT = """
Initial contact response:
[Callsign], [Facility], [Information], [Instruction]

Example: "Skyhawk November One Two Three Four Five, Airport Tower, runway 27, wind 270 at 8, cleared to land"

After initial contact through the remaining exchange:
[Shortened Callsign], [Instruction/Information]

Example: "Three Four Five, taxi via Alpha to runway 27"
    """
    
    # Readback requirements (safety-critical items)
    READBACK_REQUIRED = [
        "runway assignments",
        "runway crossings",
        "hold short instructions",
        "clearances (takeoff, landing, taxi)",
        "altimeter settings (QNH)",
        "headings",
        "altitudes",
        "speed restrictions",
        "squawk codes",
    ]
    
    # Common corrections
    COMMON_ERRORS = {
        "cleared for the approach": "cleared for approach",
        "you are cleared": "cleared",
        "roger that": "roger" or "wilco",
        "copy that": "roger" or "wilco",
        "affirmative on that": "affirmative",
        "negative on that": "negative",
    }
    
    # Wind format
    WIND_FORMAT = """
Wind direction and speed:
- Format: [Direction in degrees] at [Speed in knots]
- Example: "wind 270 at 8" or "wind 270 at 8 gusting 15"
- Calm wind: "wind calm"
- Variable: "wind variable at 3"
    """
    
    # Dutch airport specifics (from atc.instructions.md)
    DUTCH_CONVENTIONS = """
Dutch aviation specifics:
- Aircraft registration: PH-XXX or PHXXX format
- Callsign shortening: PH-CWE becomes "CWE" or "WE" in controller responses
- QNH in hectopascals (e.g., "QNH 1019")
- Distances in nautical miles (NM)
- Altitudes in feet (ft)
- Speed in knots (kt)
    """
    
    @staticmethod
    def get_phraseology_guidance() -> str:
        """Return comprehensive phraseology guidance for the critic agent."""
        return f"""
ICAO/EASA STANDARD ATC PHRASEOLOGY RULES:

1. CLEARANCE PHRASES:
Use only standard clearance phrases:
{chr(10).join(f"- {std}" for std in PhraseologyRules.CLEARANCES.keys())}

2. AVOID INFORMAL LANGUAGE:
Never use casual phrases. Replace with standard alternatives:
{chr(10).join(f"- '{informal}' → '{standard}'" for informal, standard in list(PhraseologyRules.INFORMAL_TO_STANDARD.items())[:10])}

3. RESPONSE FORMAT:
{PhraseologyRules.RESPONSE_FORMAT}

4. READBACK REQUIREMENTS:
Always require readback for:
{chr(10).join(f"- {item}" for item in PhraseologyRules.READBACK_REQUIRED)}

5. WIND FORMAT:
{PhraseologyRules.WIND_FORMAT}

6. NUMBER PRONUNCIATION:
- Use "niner" not "nine"
- Use "tree" not "three"
- Use "fife" not "five"

7. DUTCH CONVENTIONS:
{PhraseologyRules.DUTCH_CONVENTIONS}

CRITICAL: All controller communications must be clear, concise, and use only standard phraseology.
Safety depends on unambiguous communication.
"""


# Export for easy import
__all__ = ['PhraseologyRules']
