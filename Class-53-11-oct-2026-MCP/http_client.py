# import asyncio
# from mcp import Client
# from mcp.types import TextContent


# async def main():
#     async with Client("http://127.0.0.1:8000/mcp") as client:
#         print("Connected:", client.server_info)
#         print("Protocol:", client.protocol_version)

#         tools_result = await client.list_tools()
#         print("\nTOOLS")
#         for tool in tools_result.tools:
#             print("-", tool.name)

#         result = await client.call_tool(
#             "search_flights",
#             {"origin": "Bangalore", "destination": "Dubai"},
#         )

#         print("\nRESULT")
#         for block in result.content:
#             if isinstance(block, TextContent):
#                 print(block.text)


# if __name__ == "__main__":
#     asyncio.run(main())


import asyncio
from mcp import Client
from mcp.types import TextContent


async def main():

    async with Client("http://127.0.0.1:8001/mcp") as client:

        tools_result = await client.list_tools()

        print("TOOLS")

        for tool in tools_result.tools:
            print("-", tool.name)

        result = await client.call_tool(
            "search_flights",
            {
                "origin": "Bangalore",
                "destination": "Dubai"
            }
        )

        print("\nRESULT")

        for block in result.content:
            if isinstance(block, TextContent):
                print(block.text)


if __name__ == "__main__":
    asyncio.run(main())