# Enterprise Business Trip Copilot — MCP End-to-End Project

This is one connected project, not a collection of unrelated snippets.

It connects the concepts below in one business use case:

```text
USER
 ↓
AI App (app.py) - Client
 ↓
MCP Resources + Resource Template + Prompt
 ↓
LangChain Agent + GPT
 ↓
MCPAdapter
 ↓
┌──────────────────────┬──────────────────────┬─────────────────────┐
↓                      ↓                      ↓
Travel MCP             Policy MCP             Work MCP
↓                      ↓                      ↓
Tools + Resources      RAG Tool + Resource    Work Tools
↓                      ↓                      ↓
Real Weather API       OpenAI Embeddings      Demo task system
Flight Search          Semantic Retrieval
 ↓
Human Approval Gate
 ↓
Hotel Booking Tool
```

## Concepts covered

1. MCP Server
2. MCP Client
3. Tools
4. Resources
5. Resource Templates
6. Prompts
7. STDIO
8. Streamable HTTP
9. LangChain MCPAdapter
10. LLM tool calling
11. Multiple MCP servers
12. Tool name prefixing / routing
13. Real external API
14. MCP + RAG
15. Human approval before side effects
16. Remote/vendor MCP client pattern
17. ASGI deployment pattern

---

## Project structure

```text
business_trip_copilot_mcp/
│
├── app.py
├── requirements.txt
├── .env.example
│
├── servers/
│   ├── __init__.py
│   ├── travel_server.py
│   ├── policy_server.py
│   └── work_server.py
│
└── advanced/
    ├── travel_http_server.py
    ├── travel_http_client.py
    ├── asgi_app.py
    └── remote_vendor_client.py
```

---

## Setup

Create/activate a Python 3.10+ environment.

Install:

```bash
python -m pip install -U -r requirements.txt
```

Copy `.env.example` to `.env` and set:

```text
OPENAI_API_KEY=your_real_key
```

---

# Main demo

Run only:

```bash
python app.py
```

You do NOT start the three STDIO MCP servers manually.

The host launches them as subprocesses.

Example inputs:

```text
Destination [Dubai]:
Number of days [5]:
Origin [Bangalore]:
```

The app then does this:

### Step 1 — Resource

Reads:

```text
travel://preferences
```

### Step 2 — Resource Template

Reads:

```text
city://Dubai/guide
```

### Step 3 — Prompt

Gets:

```text
plan_business_trip(destination="Dubai", days="5")
```

### Step 4 — Another Resource

Reads:

```text
policy://travel-summary
```

### Step 5 — Multiple MCP servers

The LangChain MCPAdapter connects to:

```text
travel
policy
work
```

Because it is a multi-server configuration, tools are prefixed:

```text
travel_search_flights
travel_get_live_weather
travel_book_hotel

policy_search_company_policy

work_create_trip_task
work_list_trip_tasks
```

### Step 6 — Real API

The agent calls:

```text
travel_get_live_weather
```

which calls Open-Meteo.

### Step 7 — RAG

The agent calls:

```text
policy_search_company_policy
```

which:

```text
question
 ↓
OpenAI embedding
 ↓
policy document embeddings
 ↓
cosine similarity
 ↓
Top-K policy chunks
```

### Step 8 — Agentic action

The agent can call:

```text
work_create_trip_task
```

### Step 9 — Human approval

The model is intentionally NOT given:

```text
travel_book_hotel
```

The host asks:

```text
Approve booking? (yes/no)
```

Only after `yes` does the host call the side-effecting MCP tool.

This demonstrates a simple and very clear security boundary:

```text
safe/read tools
   ↓
LLM can use automatically

side-effecting booking
   ↓
human approval
   ↓
host executes
```

---

# HTTP practical

This demonstrates the SAME Travel MCP server over Streamable HTTP.

Terminal 1, from the project root:

```bash
python advanced/travel_http_server.py
```

Terminal 2:

```bash
python advanced/travel_http_client.py
```

Flow:

```text
MCP Client
 ↓
http://127.0.0.1:8000/mcp
 ↓
Travel MCP Server
```

Difference:

```text
STDIO
Client launches local server process.

HTTP
Server runs independently and the client connects to a URL.
```

---

# ASGI / deployment demo

From project root:

```bash
uvicorn advanced.asgi_app:app --host 127.0.0.1 --port 8000 --workers 4
```

Then connect to:

```text
http://127.0.0.1:8000/mcp
```

For real production use HTTPS, proper authentication, secrets management,
persistent storage, monitoring, and your normal load balancer/ingress.

---

# Vendor/remote MCP demo

Set:

```text
REMOTE_MCP_URL=https://vendor.example.com/mcp
REMOTE_MCP_TOKEN=optional-token
```

Then:

```bash
python advanced/remote_vendor_client.py
```

This is the generic pattern for connecting to an externally hosted MCP endpoint.
Actual authentication depends on the vendor; many production services use OAuth.

---

# Teaching story

Use this exact story in class:

> We are building an enterprise business-trip copilot. MCP Resources provide
> traveler preferences and fixed policy context. An MCP Prompt provides reusable
> planning instructions. MCP Tools provide actions such as flight search,
> weather lookup, semantic policy retrieval, and work-task creation. The AI Host
> connects multiple MCP servers through LangChain MCPAdapter. A RAG-style policy
> tool performs semantic retrieval. A real weather tool calls an external API.
> Finally, a hotel booking action is kept behind explicit human approval.

That connects the whole MCP mental model:

```text
TOOLS      = DO
RESOURCES  = KNOW
PROMPTS    = GUIDE
STDIO      = LOCAL TRANSPORT
HTTP       = REMOTE/DEPLOYABLE TRANSPORT
MCPAdapter = MCP TOOLS → LANGCHAIN AGENT
RAG TOOL   = DYNAMIC KNOWLEDGE RETRIEVAL
HOST       = ORCHESTRATION + SECURITY + APPROVAL
```
