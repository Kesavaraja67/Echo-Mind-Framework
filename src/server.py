from fastapi import FastAPI
from pydantic import BaseModel
import asyncio

from memory_agent.graph import graph
from memory_agent.context import Context

app = FastAPI(title="Memory Agent API")

# ----------------------------
# Health check endpoint
# ----------------------------


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Memory Agent running 🚀"}


# ----------------------------
# Chat endpoint
# ----------------------------
class ChatRequest(BaseModel):
    user_input: str
    thread_id: str = "session-1"  # allows multiple conversations


@app.post("/chat")
async def chat(request: ChatRequest):
    # Initial state
    state = {"messages": [{"role": "user", "content": request.user_input}]}

    # Context (must include thread_id for MemorySaver)
    context = Context(
        user_id="default",
        model="gpt-4",
        system_prompt="You are a helpful assistant. {user_info}\nTime: {time}",
        thread_id=request.thread_id,
    )

    # Run graph
    state = await graph.ainvoke(state, config={"configurable": {"thread_id": request.thread_id}})

    # Extract assistant responses
    assistant_replies = [msg["content"]
                         for msg in state["messages"] if msg["role"] == "assistant"]

    return {"reply": assistant_replies[-1] if assistant_replies else "(no response)"}
