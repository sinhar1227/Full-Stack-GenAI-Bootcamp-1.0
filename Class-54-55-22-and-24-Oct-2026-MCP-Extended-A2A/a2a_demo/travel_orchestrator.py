import asyncio

import httpx

from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import get_message_text, new_text_message
from a2a.types import Message, Role, SendMessageRequest


async def call_remote_agent(
    base_url: str,
    task_text: str,
) -> str:
    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )

        agent_card = await resolver.get_agent_card()

        print(f"\nDiscovered Agent: {agent_card.name}")
        print("Skills:")
        for skill in agent_card.skills:
            print("-", skill.name)

        client = await create_client(
            agent=agent_card,
            client_config=ClientConfig(
                streaming=False
            ),
        )

        try:
            message = new_text_message(
                task_text,
                role=Role.ROLE_USER,
            )

            request = SendMessageRequest(
                message=message
            )

            async for response in client.send_message(request):
                if isinstance(response, Message):
                    return get_message_text(response)

                return str(response)

        finally:
            await client.close()

    return "No response received."


async def main():
    print("=" * 65)
    print("TRAVEL ORCHESTRATOR AGENT")
    print("=" * 65)

    user_request = (
        "Plan a 5-day Dubai trip from Bangalore. "
        "I need a flight and a 4-star hotel."
    )

    print("\nUSER REQUEST:")
    print(user_request)

    flight_result = await call_remote_agent(
        "http://127.0.0.1:9999",
        "Find good flights from Bangalore to Dubai.",
    )

    hotel_result = await call_remote_agent(
        "http://127.0.0.1:10000",
        "Find a 4-star hotel in Dubai for 5 nights.",
    )

    print("\n" + "=" * 65)
    print("FLIGHT AGENT RESPONSE")
    print("=" * 65)
    print(flight_result)

    print("\n" + "=" * 65)
    print("HOTEL AGENT RESPONSE")
    print("=" * 65)
    print(hotel_result)

    print("\n" + "=" * 65)
    print("FINAL ORCHESTRATED RESULT")
    print("=" * 65)
    print(
        "Travel Orchestrator delegated work to two independent "
        "A2A agents and collected their responses."
    )


if __name__ == "__main__":
    asyncio.run(main())
