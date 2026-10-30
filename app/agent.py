"""A plain LangChain agent: Claude plus two tools. Nothing here knows about Inngest."""

import datetime
import zoneinfo

from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool

model = ChatAnthropic(model="claude-opus-5-5", max_tokens=1024)

SYSTEM = (
    "You write short, friendly greetings. Before writing, look up the person's "
    "local time and weather with the tools, then tailor the greeting to the time "
    "of day and the weather. One sentence."
)


@tool
def local_time(timezone: str) -> str:
    """Current local time in an IANA timezone, e.g. Europe/Paris."""

    return f"{datetime.datetime.now(zoneinfo.ZoneInfo(timezone)):%A %H:%M}"


@tool
def weather(city: str) -> str:
    """Current weather in a city."""

    return f"{city}: light rain"  # Stand-in for a weather API.


tools = [local_time, weather]
