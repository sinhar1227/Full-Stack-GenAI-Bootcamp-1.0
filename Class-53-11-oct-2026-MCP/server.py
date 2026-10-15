from mcp.server import MCPServer

server = MCPServer("MCP Server")

@server.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@server.tool()
def search_flights(
    origin: str,
    destination: str
) -> str:
    """Search available flights between two cities."""

    return (
        f"Available flight found from {origin} to {destination}. "
        f"Flight EK501 costs ₹28,000."
    )

@server.tool()
def book_hotel(
    city: str,
    nights: int
) -> str:
    """Book a hotel in a city."""

    return (
        f"Hotel booked in {city} "
        f"for {nights} nights."
    )
    

@server.resource("travel://preferences")
def travel_preferences() -> str:
    """Return user travel preferences."""

    return """
Preferred airline: Emirates
Preferred seat: Window
Preferred class: Economy
Preferred hotel: 4 Star
"""

@server.resource("weather://{city}")
def weather(city: str) -> str:
    """Return weather information for a city."""

    return f"Weather in {city}: Sunny, 28°C"


@server.prompt()
def plan_vacation(
    destination: str,
    days: str
) -> str:
    """Reusable vacation planning prompt."""

    return f"""
Plan a {days}-day vacation to {destination}.

Check:
1. Travel preferences
2. Flights
3. Weather
4. Hotel
"""

if __name__ == "__main__":
    server.run()