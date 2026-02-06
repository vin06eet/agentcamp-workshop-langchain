import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

load_dotenv()

SYSTEM_PROMPT = f"""You are a helpful AI assistant named Aria.
- Be friendly and conversational
- Give concise but thorough answers
- Admit when you don't know something

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
        tools=[],
        system_prompt=SYSTEM_PROMPT,
    )
    
    return agent

@cl.on_chat_start
async def start():
    agent = create_assistant_agent()
    
    cl.user_session.set("agent", agent)
    cl.user_session.set("chat_history", [])
    
    await cl.Message(content="👋 Hi! I'm Aria. How can I help?").send()

@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent")
    chat_history = cl.user_session.get("chat_history")
    
    chat_history.append({"role": "user", "content": message.content})
    
    msg = cl.Message(content="")
    full_response = ""

    async for data, _ in agent.astream(
        {"messages": chat_history}, 
        stream_mode="messages"
    ):
        chunks = data.content_blocks
        if len(chunks) > 0:
            chunk = chunks[-1]["text"]
            full_response += chunk
            await msg.stream_token(chunk)

    await msg.send()

    chat_history.append({"role": "assistant", "content": full_response})
    cl.user_session.set("chat_history", chat_history)