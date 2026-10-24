# from server import server

# if __name__ == "__main__":
#     server.run(
#         transport="streamable-http",
#         host="127.0.0.1",
#         port=8000,
#         stateless_http=True,
#         json_response=True,
#     )

from mcp.server import MCPServer

server = MCPServer("Travel MCP Server")


@server.tool()
def add(a: int, b: int) -> int:
    return a + b


@server.tool()
def search_flights(
    origin: str,
    destination: str
) -> str:
    return (
        f"Available flight found from {origin} to {destination}. "
        f"Flight EK501 costs ₹28,000."
    )


@server.tool()
def book_hotel(
    city: str,
    nights: int
) -> str:
    return f"Hotel booked in {city} for {nights} nights."


if __name__ == "__main__":
    server.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8001,
        stateless_http=True,
        json_response=True,
    )