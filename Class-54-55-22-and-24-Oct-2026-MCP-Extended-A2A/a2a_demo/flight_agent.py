import uvicorn

from a2a.helpers import get_message_text, new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from starlette.applications import Starlette

class FlightAgentExecutor(AgentExecutor):
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = get_message_text(context.message) if context.message else ""

        result = (
            "Flight Agent result:\n"
            "Bangalore -> Dubai\n"
            "1. Emirates EK569 | Non-stop | ₹28,000\n"
            "2. Air India AI995 | 1 stop | ₹24,500\n"
            f"\nReceived task: {query}"
        )

        await event_queue.enqueue_event(
            new_text_message(result)
        )

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        raise NotImplementedError("Cancellation is not supported.")


skill = AgentSkill(
    id="search_flights",
    name="Search Flights",
    description="Searches flight options between cities.",
    input_modes=["text/plain"],
    output_modes=["text/plain"],
    tags=["travel", "flight"],
    examples=["Find flights from Bangalore to Dubai"],
)

agent_card = AgentCard(
    name="Flight Agent",
    description="Specialized agent for searching flights.",
    version="1.0.0",
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    capabilities=AgentCapabilities(
        streaming=False,
        extended_agent_card=False,
    ),
    supported_interfaces=[
        AgentInterface(
            protocol_binding="JSONRPC",
            url="http://127.0.0.1:9999",
            protocol_version="1.0",
        )
    ],
    skills=[skill],
)

request_handler = DefaultRequestHandler(
    agent_executor=FlightAgentExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=agent_card,
)

app = Starlette(
    routes=[
        *create_agent_card_routes(agent_card),
        *create_jsonrpc_routes(request_handler, "/"),
    ]
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9999)
