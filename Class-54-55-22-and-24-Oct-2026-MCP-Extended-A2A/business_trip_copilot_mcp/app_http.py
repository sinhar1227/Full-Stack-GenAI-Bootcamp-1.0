import asyncio
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_openai import ChatOpenAI
from mcp import Client
from mcp.types import TextContent, TextResourceContents

load_dotenv()
TRAVEL_URL = "http://127.0.0.1:8001/mcp"
POLICY_URL = "http://127.0.0.1:8002/mcp"
WORK_URL = "http://127.0.0.1:8003/mcp"

model = ChatOpenAI(model="gpt-5.6", reasoning_effort="none")

async def read_travel_context(destination: str, days: str) -> tuple[str,str,str]:
    async with Client(TRAVEL_URL) as client:
        preferences_result = await client.read_resource("travel://preferences")
        preferences = "\n".join(item.text for item in preferences_result.contents if isinstance(item, TextResourceContents))
        city_result = await client.read_resource(f"city://{destination}/guide")
        city_context = "\n".join(item.text for item in city_result.contents if isinstance(item, TextResourceContents))
        prompt_result = await client.get_prompt("plan_business_trip", {"destination":destination,"days":days})
        planning_prompt = "\n".join(message.content.text for message in prompt_result.messages if isinstance(message.content, TextContent))
    return preferences, city_context, planning_prompt

async def read_policy_summary() -> str:
    async with Client(POLICY_URL) as client:
        result = await client.read_resource("policy://travel-summary")
        return "\n".join(item.text for item in result.contents if isinstance(item, TextResourceContents))

async def confirm_hotel_booking(city: str, nights: int, hotel_class: str) -> None:
    print("\n" + "="*70)
    print("HUMAN APPROVAL REQUIRED")
    print("="*70)
    print(f"Requested action: book {hotel_class} hotel in {city} for {nights} nights.")
    approval = input("Approve booking? (yes/no): ").strip().lower()
    if approval != "yes":
        print("Booking cancelled. No side-effecting tool was executed.")
        return
    async with Client(TRAVEL_URL) as client:
        result = await client.call_tool("book_hotel", {"city":city,"nights":nights,"hotel_class":hotel_class})
        print("\nBOOKING RESULT")
        for block in result.content:
            if isinstance(block, TextContent):
                print(block.text)

async def main():
    destination = input("Destination [Dubai]: ").strip() or "Dubai"
    days = input("Number of days [5]: ").strip() or "5"
    origin = input("Origin [Bangalore]: ").strip() or "Bangalore"

    preferences, city_context, planning_prompt = await read_travel_context(destination, days)
    policy_summary = await read_policy_summary()

    print("\n" + "="*70)
    print("MCP RESOURCE + PROMPT CONTEXT LOADED")
    print("="*70)
    print("\nTRAVEL PREFERENCES\n", preferences)
    print("\nCITY RESOURCE\n", city_context)
    print("\nPOLICY RESOURCE\n", policy_summary)
    print("\nMCP PROMPT\n", planning_prompt)

    config = {
        "mcpServers": {
            "travel": {"url": TRAVEL_URL},
            "policy": {"url": POLICY_URL},
            "work": {"url": WORK_URL},
        }
    }

    async with MCPAdapter(config) as adapter:
        discovered_tools = await adapter.list_tools()
        print("\n" + "="*70)
        print("DISCOVERED MCP TOOLS")
        print("="*70)
        for tool in discovered_tools:
            print("-", tool.name)

        agent_tools = [tool for tool in discovered_tools if tool.name != "travel_book_hotel"]

        system_prompt = f"""You are an enterprise business-trip copilot.

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
- Use work_create_trip_task to create one useful preparation task.
- You CANNOT book a hotel yourself.
- Hotel booking requires separate human approval.
- Give a concise but useful final trip plan.""".strip()

        agent = create_agent(model=model, tools=agent_tools, system_prompt=system_prompt)
        user_question = (
            f"Plan my {days}-day business trip from {origin} to {destination}. "
            "Check live weather, find a suitable flight, verify company policy for flight class and hotel category, "
            "and create one useful trip preparation task."
        )
        print("\n" + "="*70)
        print("USER REQUEST")
        print("="*70)
        print(user_question)

        result = await agent.ainvoke({"messages":[{"role":"user","content":user_question}]})

        print("\n" + "="*70)
        print("AGENT MESSAGE FLOW")
        print("="*70)
        for message in result["messages"]:
            print(f"\n{type(message).__name__}")
            print(message)

        print("\n" + "="*70)
        print("FINAL TRIP PLAN")
        print("="*70)
        print(result["messages"][-1].content)

    await confirm_hotel_booking(city=destination, nights=int(days), hotel_class="4-star")

if __name__ == "__main__":
    asyncio.run(main())
