import json
from urllib.parse import urlencode
from urllib.request import urlopen

from mcp.server import MCPServer

server = MCPServer("Business Travel MCP Server")


# ============================================================
# REAL EXTERNAL API HELPER
# ============================================================

def _get_json(url: str) -> dict:
    with urlopen(url, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


# ============================================================
# TOOLS = DO
# ============================================================

@server.tool()
def search_flights(origin: str, destination: str) -> list[dict]:
    """
    Search demo flight options.

    In a real project, replace this body with Amadeus,
    airline, GDS, or your internal travel API.
    """
    return [
        {
            "airline": "Emirates",
            "flight": "EK501",
            "origin": origin,
            "destination": destination,
            "price_inr": 28000,
            "stops": 0,
        },
        {
            "airline": "Air India",
            "flight": "AI995",
            "origin": origin,
            "destination": destination,
            "price_inr": 24500,
            "stops": 1,
        },
    ]


@server.tool()
def get_live_weather(city: str) -> dict:
    """Get live/current weather for a city using Open-Meteo."""

    geo_url = (
        "https://geocoding-api.open-meteo.com/v1/search?"
        + urlencode(
            {
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            }
        )
    )

    geo_data = _get_json(geo_url)
    locations = geo_data.get("results") or []

    if not locations:
        return {"error": f"Could not find city: {city}"}

    location = locations[0]

    weather_url = (
        "https://api.open-meteo.com/v1/forecast?"
        + urlencode(
            {
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "wind_speed_10m"
                ),
                "timezone": "auto",
            }
        )
    )

    weather_data = _get_json(weather_url)
    current = weather_data.get("current", {})

    return {
        "city": location["name"],
        "country": location.get("country"),
        "temperature_c": current.get("temperature_2m"),
        "humidity_percent": current.get("relative_humidity_2m"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
    }


@server.tool()
def book_hotel(city: str, nights: int, hotel_class: str = "4-star") -> dict:
    """
    Demo side-effecting booking tool.

    The host application intentionally keeps this tool away from
    the autonomous agent and calls it only after explicit user approval.
    """
    return {
        "status": "confirmed",
        "city": city,
        "nights": nights,
        "hotel_class": hotel_class,
        "booking_id": "HOTEL-DEMO-1001",
    }


# ============================================================
# RESOURCE = KNOW
# ============================================================

@server.resource("travel://preferences")
def travel_preferences() -> str:
    """Known user/business travel preferences."""
    return """
Preferred airline: Emirates
Preferred seat: Window
Preferred class: Economy
Preferred hotel category: 4-star
Preferred trip style: Comfortable but policy-compliant
""".strip()


# ============================================================
# RESOURCE TEMPLATE = DYNAMIC KNOW
# ============================================================

@server.resource("city://{city}/guide")
def city_guide(city: str) -> str:
    """Small dynamic city context resource."""
    return (
        f"{city} business-travel guide: "
        "keep airport transfer buffer, carry travel insurance details, "
        "and verify local meeting location before departure."
    )


# ============================================================
# PROMPT = GUIDE
# ============================================================

@server.prompt()
def plan_business_trip(destination: str, days: str) -> str:
    """Reusable instructions for planning a business trip."""
    return f"""
Plan a {days}-day business trip to {destination}.

You should:
1. Respect the traveler's preferences.
2. Check the company travel policy.
3. Check live weather.
4. Search suitable flights.
5. Recommend, but do not autonomously confirm, a hotel booking.
6. Clearly mention anything that requires human approval.
""".strip()


if __name__ == "__main__":
    # Default transport = STDIO
    server.run()
