from mcp.server import MCPServer

server = MCPServer("Work Management MCP Server")


@server.tool()
def create_trip_task(
    title: str,
    owner: str = "Sunny",
) -> dict:
    """
    Create a demo work-management task.

    Replace with Jira, Linear, GitHub Issues, ServiceNow,
    or another real provider in production.
    """
    return {
        "created": True,
        "task_id": "TRIP-101",
        "title": title,
        "owner": owner,
        "status": "open",
    }


@server.tool()
def list_trip_tasks() -> list[dict]:
    """List demo trip tasks."""
    return [
        {
            "task_id": "TRIP-100",
            "title": "Prepare conference slides",
            "owner": "Sunny",
            "status": "open",
        }
    ]


if __name__ == "__main__":
    server.run()
