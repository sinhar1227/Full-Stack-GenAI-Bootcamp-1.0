#!/usr/bin/env python
# coding: utf-8

# In[1]:


print("all ok")


# Tool calling means an LLM can decide to use an external function/tool when it needs information or wants to perform an action, instead of answering only from its own knowledge.

# Tool calling is the ability of an LLM to select and invoke external tools or functions to get information or perform actions beyond its built-in knowledge.

# ## these are some of the example 
# ### but the concept is we can convert any of the funcationality into the tool
# 
# Web search
# Calculator
# Database query
# API calls
# retriever
# Email sending
# Weather API
# Stock-price API
# File operations

# User: "What is the weather in Bangalore today?"
# 
#         ↓
# 
# LLM decides: "I need current weather data."
# 
#         ↓
# 
# Calls Weather Tool
# 
#         ↓
# 
# Tool returns: 28°C, cloudy
# 
#         ↓
# 
# LLM gives final answer

# Node = graph decides when to execute the function.
# Tool = LLM decides when to execute the function.

# User
#  ↓
# LLM
#  ↓
# Does it need a tool?
#  ↓
# Yes
#  ↓
# Tool(function) Call
#  ↓
# Tool Result
#  ↓
# LLM
#  ↓
# Final Answer

# MCP Server
#    │
#    ├── Tool 1
#    ├── Tool 2
#    └── Tool 3
#         ↓
# langchain-mcp-adapters
#         ↓
# LangChain BaseTools
#         ↓
# LangGraph Agent

# Now if the user asks: "What is 20 + 30?"
# 
# the LLM may produce a tool request like:
# 
# Tool: add
# Arguments:
# a = 20
# b = 30
# 
# Then the tool executes: 50
# 
# and the LLM can use that result to answer.

# The LLM does not execute the function itself. It decides which tool(function) to call and with what arguments; your application executes the tool and returns the result to the LLM.
# 
# LLM = decision maker
# Tool = actual executor(acutal funcationality)

# In[ ]:


from dotenv import load_dotenv
import os
load_dotenv()

print("Setup loaded.")
print("GROQ_API_KEY available:", bool(os.getenv("GROQ_API_KEY")))
print("OPENAI_API_KEY available:", bool(os.getenv("OPENAI_API_KEY")))
print("TAVILY_API_KEY available:", bool(os.getenv("TAVILY_API_KEY")))


# ## 1. `@tool` decorator

# In[3]:


from langchain_core.tools import tool


# In[4]:


@tool
def add_basic(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


# In[5]:


print("Name:", add_basic.name)


# In[6]:


print("Description:", add_basic.description)


# In[7]:


print("Args:", add_basic.args)


# In[8]:


add_basic.invoke({"a": 20, "b": 30})


# In[9]:


result = add_basic.invoke({"a": 20, "b": 30})
print("Execution result:", result)


# ## 2. `@tool("custom_name")`

# In[10]:


@tool("calculator")
def add_with_custom_name(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


# In[11]:


print("Tool name:", add_with_custom_name.name)
print("Execution result:", add_with_custom_name.invoke({"a": 10, "b": 15}))


# In[23]:


@tool(
    "multiply_numbers",
    description="Multiply two integers and return the result.",
    return_direct=False,
)
def multiply_with_options(a, b):
    return a * b


# In[24]:


print("Execution result:", multiply_with_options.invoke({"a": "sunny", "b": 7}))


# In[14]:


print("Name:", multiply_with_options.name)
print("Description:", multiply_with_options.description)
print("return_direct:", multiply_with_options.return_direct)
print("Execution result:", multiply_with_options.invoke({"a": 6, "b": 7}))


# ## 4. `@tool` with Pydantic

# In[15]:


from pydantic import BaseModel, Field, ValidationError


# In[16]:


class CalculatorInputTest(BaseModel):
    a: int = Field(description="First integer")
    b: int = Field(description="Second integer")


# In[17]:


@tool(args_schema=CalculatorInputTest)
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


# In[18]:


print("Schema:", multiply.args_schema.model_json_schema())


# In[19]:


print("Execution result:", multiply.invoke({"a": 8, "b": 9}))


# In[20]:


multiply.invoke({"a": "sunny", "b": 9})


# ## 5. `@tool(parse_docstring=True)`

# In[25]:


@tool(parse_docstring=True)
def search_with_docstring(query: str, limit: int) -> str:
    """Search documents.

    Args:
        query: Search query entered by the user.
        limit: Maximum number of results.
    """
    return f"Searching for '{query}' with limit={limit}"


# In[26]:


print("Args schema:")
print(search_with_docstring.args_schema.model_json_schema())


# In[27]:


print("Execution result:", search_with_docstring.invoke({"query": "LangGraph memory","limit": 3,}))


# ## 6. Async function with `@tool`

# In[28]:


import asyncio


# In[30]:


@tool
async def get_data_async(url: str) -> str:
    """Fetch data asynchronously."""
    await asyncio.sleep(0.1)
    return f"Data from {url}"


# In[31]:


result = await get_data_async.ainvoke({"url": "https://example.com"})
print("Async execution result:", result)


# ## 7. Tool with `ToolRuntime` 
# 
# <!-- from typing_extensions import TypedDict
# from langgraph.graph import StateGraph, MessagesState, START, END
# from langgraph.prebuilt import ToolNode, ToolRuntime
# from langchain_core.messages import AIMessage
# 
# class RuntimeState(MessagesState):
#     question: str
# 
# @tool
# def read_question_from_runtime(runtime: ToolRuntime) -> str:
#     """Read the current question from LangGraph state."""
#     return runtime.state["question"]
# 
# def create_demo_tool_call(state: RuntimeState):
#     return {
#         "messages": [
#             AIMessage(
#                 content="",
#                 tool_calls=[{
#                     "name": "read_question_from_runtime",
#                     "args": {},
#                     "id": "demo_call_1",
#                     "type": "tool_call",
#                 }],
#             )
#         ]
#     }
# 
# runtime_builder = StateGraph(RuntimeState)
# runtime_builder.add_node("create_call", create_demo_tool_call)
# runtime_builder.add_node("tools", ToolNode([read_question_from_runtime]))
# runtime_builder.add_edge(START, "create_call")
# runtime_builder.add_edge("create_call", "tools")
# runtime_builder.add_edge("tools", END)
# 
# runtime_graph = runtime_builder.compile()
# 
# runtime_result = runtime_graph.invoke({
#     "question": "What is LangGraph?",
#     "messages": [],
# })
# 
# print("Tool result:", runtime_result["messages"][-1].content) -->

# ## 8. `Tool(...)` constructor"

# In[32]:


from langchain_core.tools import Tool


# In[33]:


def simple_search_function(query: str) -> str:
    return f"Searching for {query}"


# In[35]:


simple_search_tool = Tool(
    name="simple_search",
    func=simple_search_function,
    description="Search for information.",
)


# In[36]:


print("Name:", simple_search_tool.name)
print("Execution result:", simple_search_tool.invoke("LangGraph"))


# In[37]:


def search_from_function(query: str) -> str:
    return f"Result for {query}"


# In[38]:


Tool.from_function(
    func=search_from_function,
    name="search_from_function",
    description="Search information.",
)


# In[39]:


from_function_tool = Tool.from_function(
    func=search_from_function,
    name="search_from_function",
    description="Search information.",
)


# In[40]:


print("Execution result:", from_function_tool.invoke("Agentic AI"))


# ## 10. `StructuredTool.from_function()`

# In[41]:


from langchain_core.tools import StructuredTool

def calculate_tax_test(income: float, tax_rate: float) -> float:
    return income * tax_rate

tax_tool_test = StructuredTool.from_function(
    func=calculate_tax_test,
    name="calculate_tax",
    description="Calculate tax from income and tax rate.",
)

print("Args:", tax_tool_test.args)
print("Execution result:", tax_tool_test.invoke({
    "income": 100000,
    "tax_rate": 0.20,
}))


# In[43]:


class MultiplyInputTest2(BaseModel):
    a: int = Field(description="First number")
    b: int = Field(description="Second number")
class MultiplyInputTest2(BaseModel):
    a: int = Field(description="First number")
    b: int = Field(description="Second number")

def direct_multiply(a: int, b: int) -> int:
    return a * b

direct_structured_tool = StructuredTool(
    name="direct_multiply",
    description="Multiply two numbers.",
    func=direct_multiply,
    args_schema=MultiplyInputTest2,
)

print("Execution result:", direct_structured_tool.invoke({
    "a": 12,
    "b": 4,
}))


# ## 12. Subclass `BaseTool`

# In[44]:


from typing import Type
from langchain_core.tools import BaseTool


# In[45]:


class SearchInputTest(BaseModel):
    query: str = Field(description="Search query")


# In[46]:


class MySearchToolTest(BaseTool):
    name: str = "my_search"
    description: str = "Search my custom database."
    args_schema: Type[BaseModel] = SearchInputTest

    def _run(self, query: str) -> str:
        return f"Custom database result for: {query}"


# In[47]:


custom_base_tool = MySearchToolTest()


# In[48]:


print("Execution result:", custom_base_tool.invoke({
    "query": "LangGraph state management"
}))


# ## 13. `create_retriever_tool()`

# In[ ]:


from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.tools import create_retriever_tool


# In[ ]:


class DemoRetriever(BaseRetriever):
    def _get_relevant_documents(self, query: str, *, run_manager=None):
        return [
            Document(
                page_content=f"Demo internal document relevant to: {query}",
                metadata={"source": "demo.txt"},
            )
        ]

demo_retriever = DemoRetriever()


# In[ ]:


retriever_tool_test = create_retriever_tool(
    demo_retriever,
    name="search_company_documents",
    description="Search internal company documents.",
)


# In[ ]:


print("Execution result:")
print(retriever_tool_test.invoke({
    "query": "What is the company leave policy?"
}))


# ## Model setup for schema/binding tests

# In[49]:


groq_llm = None

if os.getenv("GROQ_API_KEY"):
    from langchain_groq import ChatGroq

    groq_llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
    )
    print("Groq model initialized.")
else:
    print("Skipping live Groq tests because GROQ_API_KEY is not available.")


# In[50]:


def weather_callable(location: str) -> str:
    """Get weather for a location."""
    return f"Demo weather for {location}: 28°C"

# Local Python implementation works independently:
print("Direct Python execution:", weather_callable("Bangalore"))


# In[51]:


callable_bound_model = groq_llm.bind_tools(
    [weather_callable],
    tool_choice="weather_callable",
)

ai_message = callable_bound_model.invoke(
    "Use the weather tool for Bangalore."
)

print("Generated tool calls:")
print(ai_message.tool_calls)


# In[ ]:


class GetWeatherSchema(BaseModel):
    """Get current weather."""
    location: str = Field(description="City name")

from langchain_core.utils.function_calling import convert_to_openai_tool

print("Converted tool schema:")
print(convert_to_openai_tool(GetWeatherSchema))


# In[ ]:


pydantic_bound_model = groq_llm.bind_tools(
    [GetWeatherSchema],
    tool_choice="GetWeatherSchema",
)

ai_message = pydantic_bound_model.invoke(
    "Get the weather for Bangalore."
)

print("Generated tool call:")
print(ai_message.tool_calls)

print(
"Important: There is no weather implementation here, "
"so the returned tool call still needs an executor."
)


# In[ ]:


class WeatherTypedDict(TypedDict):
    """Get current weather."""
    location: str

print("Converted TypedDict tool schema:")
print(convert_to_openai_tool(WeatherTypedDict))


# In[ ]:


if groq_llm is not None:
    typed_dict_model = groq_llm.bind_tools(
        [WeatherTypedDict],
        tool_choice="WeatherTypedDict",
    )

    ai_message = typed_dict_model.invoke(
        "Get the weather for New York."
    )

    print("Generated tool call:")
    print(ai_message.tool_calls)


# In[ ]:


raw_weather_tool = {
    "type": "function",
    "function": {
        "name": "get_weather_raw",
        "description": "Get current weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name",
                }
            },
            "required": ["location"],
        },
    },
}

print("Raw schema:")
print(raw_weather_tool)


# In[ ]:


if groq_llm is not None:
    raw_bound_model = groq_llm.bind_tools(
        [raw_weather_tool],
        tool_choice="get_weather_raw",
    )

    ai_message = raw_bound_model.invoke(
        "Get the weather for Delhi."
    )

    print("Generated tool call:")
    print(ai_message.tool_calls)


# ##### Toolkit — a collection/factory of related tools

# In[ ]:


from langchain_core.tools import BaseToolkit

@tool
def toolkit_add(a: int, b: int) -> int:
    """Add numbers."""
    return a + b

@tool
def toolkit_multiply(a: int, b: int) -> int:
    """Multiply numbers."""
    return a * b

class DemoMathToolkit(BaseToolkit):
    def get_tools(self):
        return [
            toolkit_add,
            toolkit_multiply,
        ]

demo_toolkit = DemoMathToolkit()
toolkit_tools = demo_toolkit.get_tools()

print("Toolkit tools:", [t.name for t in toolkit_tools])
print("Add result:", toolkit_tools[0].invoke({"a": 2, "b": 3}))
print("Multiply result:", toolkit_tools[1].invoke({"a": 4, "b": 5}))


# #### Prebuilt integration tool

# In[ ]:


from langchain_tavily import TavilySearch

tavily_tool = TavilySearch(
    max_results=3,
    search_depth="basic",
    topic="general",
)

result = tavily_tool.invoke({
    "query": "What is LangGraph?"
})

print(result)


#  `bind_tools()` and `ToolNode` are NOT creation methods
# 
#  ```text
# Create Tool
#     ↓
# bind_tools()
#     ↓
# LLM generates tool_calls
#     ↓
# ToolNode executes the call
#     ↓
# ToolMessage
#     ↓
# LLM can continue
# ```

# In[ ]:


from langchain_core.messages import AIMessage
from langgraph.prebuilt import ToolNode


# In[ ]:


@tool
def subtract(a: int, b: int) -> int:
    """Subtract b from a."""
    return a - b


# In[ ]:


tool_node = ToolNode([subtract])


# In[ ]:


tool_node_result = tool_node.invoke({
    "messages": [AIMessage(content="",
                tool_calls=[{
                "name": "subtract",
                "args": {
                    "a": 100,
                    "b": 35,
                },
                "id": "call_subtract_1",
                "type": "tool_call",
            }],
        )
    ]
})


# In[ ]:


print("ToolNode result:")
print(tool_node_result)


# In[ ]:


print("Tool output:")
print(tool_node_result["messages"][-1].content)


# #### Create an MCP tool and load it into LangChain
# 
# ```bash
# uv pip install -U mcp langchain-mcp-adapters
# ```

# In[53]:


from pathlib import Path
import sys


# In[52]:


from mcp.server.fastmcp import FastMCP


# In[54]:


mcp = FastMCP("Math")


# In[55]:


@mcp.tool()
def add_mcp(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


# In[57]:


mcp.run(transport="stdio")


# In[58]:


mcp_server_path = Path("demo_math_mcp_server.py")
mcp_server_path.write_text(mcp_server_code, encoding="utf-8")

print("Created MCP server:", mcp_server_path.resolve())


# In[59]:


from langchain_mcp_adapters.client import MultiServerMCPClient


# In[ ]:


mcp_client = MultiServerMCPClient({
    "math": {
        "transport": "stdio",
        "command": sys.executable,
        "args": [str(mcp_server_path.resolve())],
    }
})


# In[ ]:


mcp_tools = await mcp_client.get_tools()


# In[ ]:


print("Loaded MCP tools:", [t.name for t in mcp_tools])


# In[ ]:


add_mcp_tool = next(
        t for t in mcp_tools
        if t.name == "add_mcp"
    )


# In[ ]:


print(
    "MCP execution result:",
    await add_mcp_tool.ainvoke({
        "a": 10,
        "b": 25,
    })
    )


# In[ ]:


server_1 = Path("demo_mcp_add_server.py")
server_2 = Path("demo_mcp_multiply_server.py")

server_1.write_text(r'''
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("AddServer")

@mcp.tool()
def remote_add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

if __name__ == "__main__":
    mcp.run(transport="stdio")
''', encoding="utf-8")

server_2.write_text(r'''
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("MultiplyServer")

@mcp.tool()
def remote_multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

if __name__ == "__main__":
    mcp.run(transport="stdio")
''', encoding="utf-8")

print("Created two MCP server files.")


# In[ ]:


from langchain_mcp_adapters.client import MultiServerMCPClient

multi_client = MultiServerMCPClient({
    "addition": {
        "transport": "stdio",
        "command": sys.executable,
        "args": [str(server_1.resolve())],
    },
    "multiplication": {
        "transport": "stdio",
        "command": sys.executable,
        "args": [str(server_2.resolve())],
    },
})

multi_tools = await multi_client.get_tools()

print("Tools loaded from multiple MCP servers:")
print([t.name for t in multi_tools])

tool_map = {
    t.name: t
    for t in multi_tools
}

print(
    "remote_add:",
    await tool_map["remote_add"].ainvoke({
        "a": 5,
        "b": 6,
    })
)

print(
    "remote_multiply:",
    await tool_map["remote_multiply"].ainvoke({
        "a": 5,
        "b": 6,
    })
)


# In[ ]:


@tool
def langchain_add_for_mcp(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


# In[ ]:


try:
    from langchain_mcp_adapters.tools import to_fastmcp

    fastmcp_tool = to_fastmcp(
        langchain_add_for_mcp
    )

    print("Converted FastMCP tool:")
    print(fastmcp_tool)

except ImportError:
    print("Install langchain-mcp-adapters to run this section.")

