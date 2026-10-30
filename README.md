# inngest-langchain example

Make a [LangChain](https://docs.langchain.com/oss/python/langchain/overview) agent durable
with [Inngest](https://www.inngest.com/docs/reference/python): add one middleware, and every
model call and tool call becomes a retried, memoized step. A failed or interrupted run resumes
where it left off instead of calling the model or the tools again.

## The integration

The agent in `app/agent.py` is plain LangChain. `app/main.py` runs it in an Inngest function:

```py
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
```

Build the middleware inside the function, list it last, wrap the agent in `durable(...)`, and
run it as usual. See the
[`inngest_langchain` README](https://github.com/inngest/inngest-py/tree/linell/inngest-langchain/pkg/inngest_langchain)
for the rules, the sync version, retries and limits.

## Run it

Requires `ANTHROPIC_API_KEY` in your environment. Until `inngest_langchain` and an `inngest`
release with `ctx.group._span` are on PyPI, it also needs a checkout of
[inngest-py](https://github.com/inngest/inngest-py) on branch `linell/inngest-langchain` next
to this repo.

```sh
make install
make dev       # Terminal 1: FastAPI app on :8000
make inngest   # Terminal 2: Inngest Dev Server on :8288
make send      # Terminal 3: trigger a run
```

Open http://localhost:8288 to watch the run. Under the `greeter` span the trace shows
`greeter/model-0`, one `greeter/tool-<tool call ID>` step per tool call, `greeter/model-1`, and
the function's output.
