import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, AIMessageChunk
from langchain_core.messages.tool import ToolMessage

from tools import TOOLS

load_dotenv()

SYSTEM_PROMPT = f"""You are a helpful AI assistant named Aria.
You have access to tools that let you fetch real-time information.

Available tools:
- get_weather: Get current weather for any city

When users ask about weather, USE the get_weather tool. Don't make up weather data.
For other questions, answer from your knowledge.

Current date: {date.today().strftime("%B %d, %Y")}
"""


def get_llm():
    return ChatOpenAI(
        model="openai/gpt-4.1-nano",
        api_key=os.getenv("GITHUB_TOKEN"),
        base_url="https://models.github.ai/inference",
        temperature=0.7,
    )


def create_assistant_agent():
    llm = get_llm()

    agent = create_agent(
        model=llm,
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent


@cl.on_chat_start
async def start():
    agent = create_assistant_agent()

    cl.user_session.set("agent", agent)
    cl.user_session.set("chat_history", [])

    await cl.Message(
        content="👋 Hi! I'm Aria. I can check the weather for you! Try: 'What's the weather in Paris?'"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent")
    chat_history = cl.user_session.get("chat_history")

    chat_history.append({"role": "user", "content": message.content})

    msg = cl.Message(content="")
    full_response = ""
    steps = {}

    async for stream_mode, data in agent.astream(
        {"messages": chat_history},
        stream_mode=["messages", "updates"]
    ):
        if stream_mode == "updates":
            for source, update in data.items():
                if source in ("model", "tools"):
                    last_msg = update["messages"][-1]

                    if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
                        for tool_call in last_msg.tool_calls:
                            step = cl.Step(f"🔧 {tool_call['name']}", type="tool")
                            step.input = tool_call["args"]
                            await step.send()
                            steps[tool_call["id"]] = step

                    if isinstance(last_msg, ToolMessage):
                        step = steps.get(last_msg.tool_call_id)
                        if step:
                            step.output = last_msg.content
                            await step.update()

        if stream_mode == "messages":
            token, _ = data
            if isinstance(token, AIMessageChunk):
                full_response += token.content
                await msg.stream_token(token.content)

    await msg.send()

    chat_history.append({"role": "assistant", "content": full_response})
    cl.user_session.set("chat_history", chat_history)