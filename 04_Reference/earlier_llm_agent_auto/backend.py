import asyncio
from time import sleep
import datetime
from dataclasses import dataclass
from typing import List, Optional
import httpx
import pytz
from pydantic_ai.agent import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Deps:
    client: httpx.AsyncClient


model = OpenAIChatModel(
    # model_name="gpt-oss:120b",
    # model_name="qwen3:30b",
    model_name="gpt-oss:20b",
    # model_name="qwen3-coder:latest",
    provider=OpenAIProvider(base_url="http://localhost:11434/v1"),
)

agent = Agent(
    model=model,
    instructions="""
You are an AI system that users can interact with to manage and control a gantry shipping container yard.
It is a gantry controlled by a plc with a camera for machine vision. You provide a HMI/interface for the user. Use tools to answer the users query or execute a command. 

If asked what you can do, you should respond with a list of tools you can use.

Tools:
- Send intruction to gantry: send_gantry_instructions
- Get Container Positions: get_container_positions 
- Get Weather: get_weather
- Get date or time: get_current_day
If no answer is found: "Say tool was fon that can match your request," and answer to the best of you abilities.

If you got information from a tool call, let the user know with "TOOLS:".
""",
    deps_type=Deps,
    retries=3,
)


@agent.tool
async def send_gantry_instructions(ctx: RunContext[Deps], instructions: str) -> str:
    if not instructions.strip():
        return "Error: Instructions Empty"
    try:
        return "Sent instructions to gantry sucessfully!"
    except Exception as e:
        return f"Error sending instructions: {str(e)}"


@agent.tool
async def get_container_positions(ctx: RunContext[Deps]) -> str:
    # Mock container positions function - replace with real API call if needed
    return "Container positions: Mock data"


@agent.tool
async def get_current_day(ctx: RunContext[Deps], query: str) -> str:
    if not query.strip():
        return "Error: Query Empty"
    try:
        spokane_tz = pytz.timezone("America/Los_Angeles")  # Spokane is in this timezone
        current_time = datetime.datetime.now(spokane_tz)
        return f"Current date and time in Spokane: {current_time}"
    except Exception as e:
        return f"Error getting current time: {str(e)}"


@agent.tool
async def get_weather(ctx: RunContext[Deps], location: str) -> str:
    # Mock weather function - replace with real API call if needed
    return (
        f"Weather information for {location}: Currently 72°F, partly cloudy (mock data)"
    )


# Create dependencies
deps = Deps(client=httpx.AsyncClient())

# Convert to AG-UI app
app = agent.to_ag_ui(deps=deps)

if __name__ == "__main__":
    print("🤖 Starting AI Agent Server on port 4124...")
    print("🔗 AG-UI interface: http://IP:4124")
    uvicorn.run(app, host="0.0.0.0", port=4124)
