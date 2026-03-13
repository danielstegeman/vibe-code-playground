class PilotRequest:
    def __init__(self):
        self.parts = []
    
    def with_callsign(self, callsign):
        self.parts.append(f"PILOT: {callsign}")
        return self
    
    def with_position(self, position):
        self.parts.append(f"Position: {position}")
        return self
    
    def with_intention(self, intention):
        self.parts.append(f"Intention: {intention}")
        return self
    
    def with_request(self, request):
        self.parts.append(f"Request: {request}")
        return self
    
    def with_any(self, info):
        self.parts.append(info)
        return self
    
    def build(self):
        return ", ".join(self.parts)


class ControllerResponse:
    def __init__(self):
        self.parts = []
    
    def with_instruction(self, instruction):
        self.parts.append(f"CONTROLLER: {instruction}")
        return self
    
    def with_information(self, info):
        self.parts.append(f"Information: {info}")
        return self
    
    def with_expected_readback(self, readback):
        self.parts.append(f"EXPECTED READBACK: {readback}\n Note: Pilots must read back correctly. DO NOT RESPOND if readback is incorrect. If readback is incorrect, repeat original instruction.")
        return self
    
    def with_any(self, info):
        self.parts.append(info)
        return self
    
    def build(self):
        return ", ".join(self.parts)


class RadioExchange:
    def __init__(self):
        self.pilot_request_builder = None
        self.controller_response_builder = None
    
    def pilot_request(self, pilot_request_builder):
        self.pilot_request_builder = pilot_request_builder
        return self
    
    def with_controller_response(self, controller_response_builder):
        self.controller_response_builder = controller_response_builder
        return self
    
    def build(self):
        lines = []
        if self.pilot_request_builder:
            lines.append(self.pilot_request_builder.build())
        if self.controller_response_builder:
            lines.append(self.controller_response_builder.build())
        return "\n".join(lines)
    
    def __str__(self):
        return self.build()


def main():
    radio_exchange = RadioExchange().pilot_request(
        PilotRequest()
            .with_callsign("N12345")
            .with_position("10 miles south")
            .with_intention("inbound for landing")
            .with_any("VFR")
            .with_request("airport advisory")
    ).with_controller_response(
        ControllerResponse()
            .with_instruction("Enter left downwind runway 27")
            .with_information("Wind 270 at 8, altimeter 30.12")
            .with_expected_readback("Left downwind runway 27, N12345")
            .with_any("Report midfield downwind")
    )
    
    print(radio_exchange.build())
    print("\n" + "="*50 + "\n")
    print("Using __str__:")
    print(radio_exchange)


if __name__ == "__main__":
    main()