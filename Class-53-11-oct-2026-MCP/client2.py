import asyncio
from pathlib import Path

from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
load_dotenv()

model = ChatOpenAI(
    model="gpt-5.6",
    reasoning_effort="none"
)

async def main():
    server_path = Path(__file__).parent / "server.py"
    print("MCP Server:")
    print(server_path)
    
    async with MCPAdapter(server_path) as adapter:
        tools = await adapter.list_tools()
        print("\nAvailable MCP Tools:")
        
        for tool in tools:
            print("-", tool.name)
            
        agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=(
                "You are a helpful travel assistant. "
                "Use the available tools whenever required."
            )
        )
        
        user_question = (
            "Find me a flight from Bangalore to Dubai."
        )

        print("\nUSER:")
        print(user_question)
        
        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_question
                    }
                ]
            }
        )
        
        print("\n" + "=" * 60)
        print("MESSAGE FLOW")
        print("=" * 60)


        for message in result["messages"]:

            print(
                "\n",
                type(message).__name__
            )

            print(message)
            
        print("\n" + "=" * 60)
        print("FINAL ANSWER")
        print("=" * 60)

        print(
            result["messages"][-1].content
        )
        
    
if __name__ == "__main__":
    asyncio.run(main())       
            

        
    