import uvicorn

from a2a.helpers import get_message_text, new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from starlette.applications import Starlette


class HotelAgentExecutor(AgentExecutor):
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = get_message_text(context.message) if context.message else ""

        result = (
            "Hotel Agent result:\n"
            "Dubai, 5 nights\n"
            "1. Business Bay Hotel | 4-star | ₹9,500/night\n"
            "2. Downtown Executive Hotel | 4-star | ₹11,000/night\n"
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
    id="find_hotels",
    name="Find Hotels",
    description="Finds hotel options for a destination.",
    input_modes=["text/plain"],
    output_modes=["text/plain"],
    tags=["travel", "hotel"],
    examples=["Find a 4-star hotel in Dubai"],
)

agent_card = AgentCard(
    name="Hotel Agent",
    description="Specialized agent for finding hotels.",
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
            url="http://127.0.0.1:10000",
            protocol_version="1.0",
        )
    ],
    skills=[skill],
)

request_handler = DefaultRequestHandler(
    agent_executor=HotelAgentExecutor(),
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
    uvicorn.run(app, host="127.0.0.1", port=10000)
