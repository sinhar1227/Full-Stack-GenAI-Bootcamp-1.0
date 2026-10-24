import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_openai import ChatOpenAI
from mcp import Client, StdioServerParameters
from mcp.types import TextContent, TextResourceContents

load_dotenv()

BASE_DIR = Path(__file__).parent
TRAVEL_SERVER = BASE_DIR / "servers" / "travel_server.py"
POLICY_SERVER = BASE_DIR / "servers" / "policy_server.py"
WORK_SERVER = BASE_DIR / "servers" / "work_server.py"

model = ChatOpenAI(
    model="gpt-5.6",
    reasoning_effort="none",
)


async def read_travel_context(
    destination: str,
    days: str,
) -> tuple[str, str, str]:
    """
    Pure MCP Client usage:
    - Resource
    - Resource Template
    - Prompt

    The HOST explicitly reads these primitives.
    They do not automatically enter the LLM.
    """

    params = StdioServerParameters(
        command=sys.executable,
        args=[str(TRAVEL_SERVER)],
    )

    async with Client(params) as client:
        preferences_result = await client.read_resource(
            "travel://preferences"
        )

        preferences = "\n".join(
            item.text
            for item in preferences_result.contents
            if isinstance(item, TextResourceContents)
        )

        city_result = await client.read_resource(
            f"city://{destination}/guide"
        )

        city_context = "\n".join(
            item.text
            for item in city_result.contents
            if isinstance(item, TextResourceContents)
        )

        prompt_result = await client.get_prompt(
            "plan_business_trip",
            {
                "destination": destination,
                "days": days,
            },
        )

        planning_prompt = "\n".join(
            message.content.text
            for message in prompt_result.messages
            if isinstance(message.content, TextContent)
        )

    return preferences, city_context, planning_prompt


async def read_policy_summary() -> str:
    """Read a fixed MCP Resource from the policy server."""

    params = StdioServerParameters(
        command=sys.executable,
        args=[str(POLICY_SERVER)],
    )

    async with Client(params) as client:
        result = await client.read_resource(
            "policy://travel-summary"
        )

        return "\n".join(
            item.text
            for item in result.contents
            if isinstance(item, TextResourceContents)
        )


async def confirm_hotel_booking(
    city: str,
    nights: int,
    hotel_class: str,
) -> None:
    """
    Human approval gate.

    The autonomous LangChain agent does NOT receive book_hotel.
    Only this host function can call it after explicit user approval.
    """

    print("\n" + "=" * 70)
    print("HUMAN APPROVAL REQUIRED")
    print("=" * 70)
    print(
        f"Requested action: book {hotel_class} hotel "
        f"in {city} for {nights} nights."
    )

    approval = input("Approve booking? (yes/no): ").strip().lower()

    if approval != "yes":
        print("Booking cancelled. No side-effecting tool was executed.")
        return

    params = StdioServerParameters(
        command=sys.executable,
        args=[str(TRAVEL_SERVER)],
    )

    async with Client(params) as client:
        result = await client.call_tool(
            "book_hotel",
            {
                "city": city,
                "nights": nights,
                "hotel_class": hotel_class,
            },
        )

        print("\nBOOKING RESULT")
        for block in result.content:
            if isinstance(block, TextContent):
                print(block.text)


async def main():
    destination = input("Destination [Dubai]: ").strip() or "Dubai"
    days = input("Number of days [5]: ").strip() or "5"
    origin = input("Origin [Bangalore]: ").strip() or "Bangalore"

    # ========================================================
    # MCP RESOURCES + MCP PROMPT
    # ========================================================

    preferences, city_context, planning_prompt = await read_travel_context(
        destination,
        days,
    )

    policy_summary = await read_policy_summary()

    print("\n" + "=" * 70)
    print("MCP RESOURCE + PROMPT CONTEXT LOADED")
    print("=" * 70)
    print("\nTRAVEL PREFERENCES\n", preferences)
    print("\nCITY RESOURCE\n", city_context)
    print("\nPOLICY RESOURCE\n", policy_summary)
    print("\nMCP PROMPT\n", planning_prompt)

    # ========================================================
    # MULTI-SERVER MCP TOOL FLEET
    # ========================================================

    config = {
        "mcpServers": {
            "travel": {
                "command": sys.executable,
                "args": [str(TRAVEL_SERVER)],
            },
            "policy": {
                "command": sys.executable,
                "args": [str(POLICY_SERVER)],
            },
            "work": {
                "command": sys.executable,
                "args": [str(WORK_SERVER)],
            },
        }
    }

    async with MCPAdapter(config) as adapter:
        discovered_tools = await adapter.list_tools()

        print("\n" + "=" * 70)
        print("DISCOVERED MCP TOOLS")
        print("=" * 70)

        for tool in discovered_tools:
            print("-", tool.name)

        # Security pattern:
        # Do not give the autonomous model the side-effecting booking tool.
        agent_tools = [
            tool
            for tool in discovered_tools
            if tool.name != "travel_book_hotel"
        ]

        system_prompt = f"""
You are an enterprise business-trip copilot.

MCP RESOURCE: Traveler preferences
{preferences}

MCP RESOURCE: Destination context
{city_context}

MCP RESOURCE: Company travel summary
{policy_summary}

MCP PROMPT:
{planning_prompt}

Rules:
- Use travel_get_live_weather for current weather.
- Use travel_search_flights for available flight options.
- Use policy_search_company_policy when policy details need semantic retrieval.
- You may use work_create_trip_task if a useful preparation task should be created.
- You CANNOT book a hotel yourself. Hotel booking requires separate human approval.
- Give a concise but useful final plan.
""".strip()

        agent = create_agent(
            model=model,
            tools=agent_tools,
            system_prompt=system_prompt,
        )

        user_question = (
            f"Plan my {days}-day business trip from {origin} to {destination}. "
            "Check live weather, find a suitable flight, verify company policy "
            "for flight class and hotel category, and create one useful trip "
            "preparation task."
        )

        print("\n" + "=" * 70)
        print("USER REQUEST")
        print("=" * 70)
        print(user_question)

        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_question,
                    }
                ]
            }
        )

        print("\n" + "=" * 70)
        print("AGENT MESSAGE FLOW")
        print("=" * 70)

        for message in result["messages"]:
            print(f"\n{type(message).__name__}")
            print(message)

        print("\n" + "=" * 70)
        print("FINAL TRIP PLAN")
        print("=" * 70)
        print(result["messages"][-1].content)

    # ========================================================
    # HUMAN APPROVAL + SIDE EFFECT
    # ========================================================

    await confirm_hotel_booking(
        city=destination,
        nights=int(days),
        hotel_class="4-star",
    )


if __name__ == "__main__":
    asyncio.run(main())
