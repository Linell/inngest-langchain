"""An Inngest function that runs the agent durably, served by FastAPI."""

import inngest
import inngest.fast_api
from fastapi import FastAPI
from inngest_langchain import InngestMiddleware, durable
from langchain.agents import create_agent

from app.agent import SYSTEM, model, tools

inngest_client = inngest.Inngest(app_id="inngest-langchain")


@inngest_client.create_function(
    fn_id="greet",
    trigger=inngest.TriggerEvent(event="demo/greeting.requested"),
)
async def greet_fn(ctx: inngest.Context) -> str:
    name, city, language = (ctx.event.data[k] for k in ("name", "city", "language"))
    agent = durable(
        create_agent(
            model,
            tools=tools,
            system_prompt=SYSTEM,
            middleware=[InngestMiddleware(ctx, agent_id="greeter")],  # list it last
        )
    )
    prompt = f"Greet {name}, who is in {city}, in {language}."
    result = await agent.ainvoke({"messages": [("user", prompt)]})
    return result["messages"][-1].text


app = FastAPI()
inngest.fast_api.serve(app, inngest_client, [greet_fn])
