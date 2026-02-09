try:
    from .radioExchange import RadioExchange, PilotRequest, ControllerResponse
except ImportError:
    from radioExchange import RadioExchange, PilotRequest, ControllerResponse

from typing import Any
from google.adk.tools import ToolContext


class DeliveryProcedure:
    def __init__(self, aircraft_type, position, flight_rules, intention, atis_info, callsign, runway, qnh):
        self.aircraft_type = aircraft_type
        self.position = position
        self.flight_rules = flight_rules
        self.intention = intention
        self.atis_info = atis_info
        self.callsign = callsign
        self.runway = runway
        self.qnh = qnh
    
    def _get_shortened_callsign(self):
        """Extract the suffix from the callsign for controller response.
        For PH-CWE or PHCWE, returns CWE or WE depending on length.
        """
        callsign = self.callsign.replace("-", "").replace(" ", "")
        if callsign.startswith("PH"):
            return callsign[2:]
        return callsign[-3:] if len(callsign) >= 3 else callsign
    
    def build(self):
        """Build the complete delivery procedure radio exchange."""
        shortened_callsign = self._get_shortened_callsign()
        
        exchange = RadioExchange().pilot_request(
            PilotRequest()
                .with_callsign(self.callsign)
                .with_any(self.aircraft_type)
                .with_position(self.position)
                .with_any(self.flight_rules)
                .with_intention(self.intention)
                .with_any(f"Information {self.atis_info}")
                .with_request("request start-up")
        ).with_controller_response(
            ControllerResponse()
                .with_instruction(shortened_callsign)
                .with_any(f"Information {self.atis_info} correct")
                .with_any("Start-up approved")
                .with_any(f"Runway {self.runway}")
                .with_any(f"QNH {self.qnh}")
                .with_expected_readback(f"Start-up approved, Runway {self.runway}, QNH {self.qnh}, {shortened_callsign}")
        )
        
        return exchange
    
    @staticmethod
    def startup_clearance(aircraft_type, position, intention, atis_info, callsign, runway, qnh):
        """Convenience factory method for VFR startup clearance."""
        return DeliveryProcedure(
            aircraft_type=aircraft_type,
            position=position,
            flight_rules="VFR",
            intention=intention,
            atis_info=atis_info,
            callsign=callsign,
            runway=runway,
            qnh=qnh
        )


def get_delivery_clearance_procedure(
    tool_context: ToolContext,
    aircraft_type: str,
    aircraft_callsign: str,
    position: str,
    intention: str,
    atis_info: str,
    runway: str,
    qnh: str,
) -> dict[str, Any]:
    """Provide delivery/startup clearance procedure and phraseology.
    
    Use this tool when a pilot requests startup clearance from delivery.
    Provides the complete radio exchange including initial call, controller response, and expected readback.
    
    Args:
        tool_context: ADK tool context
        aircraft_type: Type of aircraft (e.g., "Cessna 152", "Piper Cherokee")
        aircraft_callsign: Aircraft callsign (e.g., "PHCWE", "PH-ABC")
        position: Aircraft location (e.g., "in front of the tower", "at the ramp")
        intention: Flight intention (e.g., "One-hour circuit and touch-and-goes")
        atis_info: ATIS information letter (e.g., "G", "Alpha")
        runway: Runway in use (e.g., "24", "09")
        qnh: QNH altimeter setting in hectopascals (e.g., "1019", "1013")
    
    Returns:
        Dictionary with delivery clearance information and complete radio exchange
    """
    delivery = DeliveryProcedure.startup_clearance(
        aircraft_type=aircraft_type,
        position=position,
        intention=intention,
        atis_info=atis_info,
        callsign=aircraft_callsign,
        runway=runway,
        qnh=qnh
    )
    
    exchange = delivery.build()
    
    return {
        "procedure_type": "delivery_clearance",
        "expected_radio_exchange": str(exchange)
    }


def main():
    """Example usage matching the syllabus."""
    delivery = DeliveryProcedure(
        aircraft_type="Cessna 152",
        position="in front of the tower",
        flight_rules="VFR",
        intention="One-hour circuit and touch-and-goes",
        atis_info="G",
        callsign="PHCWE",
        runway="24",
        qnh="1019"
    )
    
    radio_exchange = delivery.build()
    print("=== Delivery Procedure Exchange ===")
    print(radio_exchange)
    print("\n" + "="*50 + "\n")
    
    # Using convenience factory
    delivery2 = DeliveryProcedure.startup_clearance(
        aircraft_type="Cessna 152",
        position="in front of the tower",
        intention="One-hour circuit and touch-and-goes",
        atis_info="G",
        callsign="PHCWE",
        runway="24",
        qnh="1019"
    )
    
    print("=== Using Factory Method ===")
    print(delivery2.build())


if __name__ == "__main__":
    main()
