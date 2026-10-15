from mcp import Client, StdioServerParameters
from mcp.types import TextContent, TextResourceContents
import asyncio
import sys
from pathlib import Path

async def main():
    server_path = Path(__file__).parent / "server.py"
    
    server = StdioServerParameters(
    command=sys.executable,
    args=[str(server_path)]
    )
    
    async with Client(server) as client:
        print("=" * 60)
        print("CONNECTED TO MCP SERVER")
        print("=" * 60)

        print("Protocol Version:")
        print(client.protocol_version)

        print("\nServer:")
        print(client.server_info)
        
        print("\n" + "=" * 60)
        print("TOOLS")
        print("=" * 60)
        
        tools_result = await client.list_tools()
        for tool in tools_result.tools:
            print("-", tool.name)
            
        print("\n" + "=" * 60)
        print("CALL TOOL")
        print("=" * 60)

        tool_result = await client.call_tool(
            "search_flights",
            {
                "origin": "Bangalore",
                "destination": "Dubai"
            }
        )

        for block in tool_result.content:
            if isinstance(block, TextContent):
                print(block.text)
        
        
        print("\n" + "=" * 60)
        print("DIRECT RESOURCES")
        print("=" * 60)

        resources_result = await client.list_resources()

        for resource in resources_result.resources:
            print("-", resource.uri)
            
        print("\n" + "=" * 60)
        print("TRAVEL PREFERENCES")
        print("=" * 60)

        resource_result = await client.read_resource(
            "travel://preferences"
        )

        for content in resource_result.contents:
            if isinstance(content, TextResourceContents):
                print(content.text)
                
        print("\n" + "=" * 60)
        print("RESOURCE TEMPLATES")
        print("=" * 60)

        templates_result = await client.list_resource_templates()

        for template in templates_result.resource_templates:
            print("-", template.uri_template)
            
        print("\n" + "=" * 60)
        print("WEATHER RESOURCE")
        print("=" * 60)

        weather_result = await client.read_resource(
            "weather://Dubai"
        )

        for content in weather_result.contents:
            if isinstance(content, TextResourceContents):
                print(content.text)
                
        print("\n" + "=" * 60)
        print("PROMPTS")
        print("=" * 60)

        prompts_result = await client.list_prompts()

        for prompt in prompts_result.prompts:
            print("-", prompt.name)
            
        print("VACATION PROMPT")
        print("=" * 60)

        prompt_result = await client.get_prompt(
            "plan_vacation",
            {
                "destination": "Dubai",
                "days": "5"
            }
        )

        for message in prompt_result.messages:

            if isinstance(message.content, TextContent):
                print(message.content.text)
    
if __name__ == "__main__":
    asyncio.run(main())
    
# WITHOUT async

# Program
#   ↓
# Call API / MCP Server
#   ↓
# WAIT.............
#   ↓
# Response comes
#   ↓
# Next task starts

# WITH async

# Task 1 → Call API ──────── waiting
#               │
#               ├── meanwhile → Task 2 runs
#               ├── meanwhile → Task 3 runs
#               │
# Response ←────┘