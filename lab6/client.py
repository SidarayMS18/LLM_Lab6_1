"""
Expt 1 - Personal Assistant Client

Connects to server.py over stdio, discovers its MCP tools, and lets the user
chat. An LLM decides whether to call save_note, search_notes, etc.

Usage:
    Put GROQ_API_KEY=gsk_... in lab6/.env (or the project root .env / .env.local),
    or export it in your shell, then:
    python client.py

Optional env vars:
    LLM_MODEL  (default: openai/gpt-oss-120b; any Groq model with tool calling works)
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from groq import Groq

HERE = Path(__file__).parent
# Load the key from lab6/.env first, then fall back to the project root env files.
for env_file in (
    HERE / ".env",
    HERE.parent / ".env.local",
    HERE.parent / ".env.development.local",
    HERE.parent / ".env",
):
    if env_file.exists():
        load_dotenv(env_file, override=False)

SERVER_PATH = HERE / "server.py"
MODEL = os.environ.get("LLM_MODEL", "openai/gpt-oss-120b")

SYSTEM_PROMPT = """You are a personal assistant with persistent memory.
You have tools to save, search, list, update and delete the user's notes.

Rules:
- If the user tells you something to remember (facts, plans, deadlines, preferences),
  call save_note with a concise content string and 1-3 relevant tags.
- If the user asks a question about something they may have mentioned before,
  call search_notes first, then answer using ONLY the returned notes.
  If nothing is found, say you have no memory of it.
- Keep replies short and conversational.
"""


def mcp_tools_to_groq(tools) -> list[dict]:
    """Convert MCP tool definitions into Groq function-calling schema."""
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description or "",
                "parameters": t.inputSchema,
            },
        }
        for t in tools
    ]


def tool_result_text(result) -> str:
    return "\n".join(c.text for c in result.content if getattr(c, "text", None)) or "(no output)"


async def run_turn(llm: Groq, session: ClientSession, tools: list[dict], messages: list[dict]) -> str:
    """Run one user turn, looping while the model keeps requesting tool calls."""
    while True:
        response = llm.chat.completions.create(
            model=MODEL, messages=messages, tools=tools, tool_choice="auto"
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content or ""})
            return msg.content or ""

        messages.append(
            {
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in msg.tool_calls
                ],
            }
        )

        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments or "{}")
            print(f"  -> calling {tc.function.name}({json.dumps(args)})")
            result = await session.call_tool(tc.function.name, args)
            output = tool_result_text(result)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": output})


async def main() -> None:
    if not os.environ.get("GROQ_API_KEY"):
        sys.exit(
            "GROQ_API_KEY not found. Copy lab6/.env.example to lab6/.env and paste your key "
            "(get one at console.groq.com), or export it in your shell."
        )

    server_params = StdioServerParameters(command=sys.executable, args=[str(SERVER_PATH)])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = (await session.list_tools()).tools
            tools = mcp_tools_to_groq(mcp_tools)
            print("Connected to memory server. Tools:", ", ".join(t.name for t in mcp_tools))
            print(f"Using Groq model: {MODEL}. Type 'quit' to exit.\n")

            llm = Groq()
            messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

            while True:
                try:
                    user = input("You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if not user:
                    continue
                if user.lower() in {"quit", "exit"}:
                    break

                messages.append({"role": "user", "content": user})
                reply = await run_turn(llm, session, tools, messages)
                print(f"Assistant: {reply}\n")


if __name__ == "__main__":
    asyncio.run(main())
