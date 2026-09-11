import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# MODEL = "llama-3.3-70b-versatile"
MODEL = "openai/gpt-oss-20b"

def call_llm(
    messages,
    tools=None
):

    kwargs = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.2
    }

    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    response = client.chat.completions.create(
        **kwargs
    )

    return response

def ask_llm(messages):

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2
    )

    return response.choices[0].message.content

def ask_agent(messages, tools):

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.2
    )

    return response.choices[0].message