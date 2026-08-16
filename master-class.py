#!/usr/bin/env python
# coding: utf-8

# In[1]:


print("all ok")


# In[2]:


from mcp.server import MCPServer


# In[3]:


mcp = MCPServer("My MCP Server")


# In[4]:


mcp


# In[6]:


from mcp.server import MCPServer


# In[7]:


mcp = MCPServer("Calculator Server")


# In[14]:


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


# In[16]:


add(a=10, b=20)


# In[17]:


from mcp.server import MCPServer

mcp = MCPServer("Company Server")


@mcp.resource("company://policy")
def company_policy() -> str:
    return """
    Employees can work from home
    two days per week.
    """


# company://policy
#         ↓
#    MCP Resource
#         ↓
# Company policy data

# In[ ]:


# Tool     → execute something
# Resource → read something


# In[18]:


@mcp.resource("customer://{customer_id}")
def get_customer(customer_id: str) -> str:
    return f"Customer information for {customer_id}"


# In[19]:


get_customer(customer_id="12345")


# In[20]:


from mcp.server import MCPServer

mcp = MCPServer("Travel Server")


@mcp.tool()
def search_flights(
    origin: str,
    destination: str
) -> str:
    """Search flights between two cities."""

    return (
        f"Available flights from "
        f"{origin} to {destination}"
    )


@mcp.resource("travel://preferences")
def travel_preferences() -> str:
    """Return user's travel preferences."""

    return """
    Preferred airline: Emirates
    Preferred seat: Window
    Preferred class: Economy
    """


# Now the MCP server exposes:
# 
# Travel MCP Server
# 
# ├── TOOL
# │   └── search_flights()
# │
# └── RESOURCE
#     └── travel://preferences

# In[ ]:


# Conceptually, we can also expose reusable prompts such as:


# In[ ]:


@mcp.prompt()
def plan_vacation(
    destination: str,
    days: int
) -> str:
    return f"""
    Plan a {days}-day vacation to {destination}.

    Consider:
    - Flights
    - Hotels
    - Weather
    - Activities
    """


# Tool
# → search_flights()
# 
# Resource
# → travel://preferences
# 
# Prompt
# → plan_vacation()

# In[ ]:


from mcp.server import MCPServer


mcp = MCPServer("Travel MCP Server")


# -------------------------
# TOOL
# -------------------------

@mcp.tool()
def search_flights(
    origin: str,
    destination: str
) -> str:
    """Search available flights."""

    return (
        f"Flights found from "
        f"{origin} to {destination}"
    )


@mcp.tool()
def book_hotel(
    city: str,
    nights: int
) -> str:
    """Book a hotel."""

    return (
        f"Hotel booked in {city} "
        f"for {nights} nights."
    )


# -------------------------
# RESOURCE
# -------------------------

@mcp.resource("travel://preferences")
def travel_preferences() -> str:
    """User travel preferences."""

    return """
    Airline: Emirates
    Seat: Window
    Hotel: 4 Star
    """


# -------------------------
# RESOURCE TEMPLATE
# -------------------------

@mcp.resource("weather://{city}")
def weather(city: str) -> str:
    """Weather information."""

    return f"Weather information for {city}"


# -------------------------
# PROMPT
# -------------------------

@mcp.prompt()
def plan_vacation(
    destination: str,
    days: int
) -> str:
    """Vacation planning prompt."""

    return f"""
    Plan a {days}-day trip to {destination}.

    Check:
    1. Travel preferences
    2. Flights
    3. Weather
    4. Hotel
    """


# Travel MCP Server
# │
# ├── Tools
# │   ├── search_flights()
# │   └── book_hotel()
# │
# ├── Resources
# │   ├── travel://preferences
# │   └── weather://{city}
# │
# └── Prompt
#     └── plan_vacation()

# In[ ]:


import asyncio

from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    server = StdioServerParameters(
        command="python",
        args=["server.py"]
    )

    async with Client(
        stdio_client(server)
    ) as client:

        tools = await client.list_tools()

        print(tools)


asyncio.run(main())


# In[ ]:


result = await client.call_tool(
    "search_flights",
    {
        "origin": "Bangalore",
        "destination": "Dubai"
    }
)

print(result)


# client.list_tools()
#         ↓
#     MCP Server
#         ↓
# available tools

# MCP Client
#     ↓
# call_tool()
#     ↓
# MCP Server
#     ↓
# search_flights()
#     ↓
# Result

# In[ ]:





# In[ ]:





# In[ ]:




