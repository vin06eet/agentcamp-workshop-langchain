import os
import chainlit as cl
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()

SYSTEM_PROMPT = """You are a helpful AI assistant named Aria. 
Be friendly and concise."""

def get_llm():
    return ChatOpenAI(
        model="openai/gpt-4.1-nano",
        api_key=os.getenv("GITHUB_TOKEN"),
        base_url="https://models.github.ai/inference",
        streaming=True,  # ADD THIS!
    )

@cl.on_chat_start
async def start():
    # Initialize chat history with system prompt
    cl.user_session.set("chat_history", [SystemMessage(content=SYSTEM_PROMPT)])
    await cl.Message(content="👋 Hi! I'm Aria. How can I help?").send()

@cl.on_message
async def main(message: cl.Message):
    llm = get_llm()
    chat_history = cl.user_session.get("chat_history")
    
    chat_history.append(HumanMessage(content=message.content))
    
    # Create empty message for streaming
    msg = cl.Message(content="")
    full_response = ""
    
    # Stream token by token
    async for chunk in llm.astream(chat_history):
        if chunk.content:
            full_response += chunk.content
            await msg.stream_token(chunk.content)
    
    await msg.send()
    
    chat_history.append(AIMessage(content=full_response))
    cl.user_session.set("chat_history", chat_history)