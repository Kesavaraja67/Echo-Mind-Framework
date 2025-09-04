"""Graphs that extract memories on a schedule."""

import asyncio
import logging
from datetime import datetime
from typing import cast
import uuid  # ✅ for unique thread_id

from langchain.chat_models import init_chat_model
from langgraph.graph import END, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.base import BaseStore
from langgraph.checkpoint.memory import MemorySaver

from memory_agent import tools, utils
from memory_agent.context import Context
from memory_agent.state import State

logger = logging.getLogger(__name__)

# Initialize the language model to be used for memory extraction
llm = init_chat_model()


async def call_model(state: State, runtime: Runtime[Context]) -> dict:
    """Extract the user's state from the conversation and update the memory."""
    user_id = runtime.context.user_id
    model = runtime.context.model
    system_prompt = runtime.context.system_prompt

    # Retrieve the most recent memories for context
    memories = await cast(BaseStore, runtime.store).asearch(
        ("memories", user_id),
        query=str([m.content for m in state.messages[-3:]]),
        limit=10,
    )

    # Format memories for inclusion in the prompt
    formatted = "\n".join(
        f"[{mem.key}]: {mem.value} (similarity: {mem.score})" for mem in memories
    )
    if formatted:
        formatted = f"""
<memories>
{formatted}
</memories>"""

    # Prepare the system prompt with user memories and current time
    sys = system_prompt.format(
        user_info=formatted, time=datetime.now().isoformat()
    )

    # Invoke the language model with the prepared prompt and tools
    msg = await llm.bind_tools([tools.upsert_memory]).ainvoke(
        [{"role": "system", "content": sys}, *state.messages],
        context=utils.split_model_and_provider(model),
    )
    return {"messages": [msg]}


async def store_memory(state: State, runtime: Runtime[Context]):
    # Extract tool calls from the last message
    tool_calls = getattr(state.messages[-1], "tool_calls", [])

    # Concurrently execute all upsert_memory calls
    saved_memories = await asyncio.gather(
        *(
            tools.upsert_memory(
                **tc["args"],
                user_id=runtime.context.user_id,
                store=cast(BaseStore, runtime.store),
            )
            for tc in tool_calls
        )
    )

    # Format the results of memory storage operations
    results = [
        {
            "role": "tool",
            "content": mem,
            "tool_call_id": tc["id"],
        }
        for tc, mem in zip(tool_calls, saved_memories)
    ]
    return {"messages": results}


def route_message(state: State):
    """Determine the next step based on the presence of tool calls."""
    msg = state.messages[-1]
    if getattr(msg, "tool_calls", None):
        return "store_memory"
    return END


# ------------------------------
# Build the graph
# ------------------------------
builder = StateGraph(State, context_schema=Context)

builder.add_node("call_model", call_model)
builder.add_edge("__start__", "call_model")
builder.add_node("store_memory", store_memory)
builder.add_conditional_edges(
    "call_model", route_message, ["store_memory", END]
)
builder.add_edge("store_memory", "call_model")

# Attach memory saver here
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
graph.name = "MemoryAgent"

__all__ = ["graph"]

# ------------------------------
# Run interactively
# ------------------------------
if __name__ == "__main__":

    async def chat():
        print("🤖 Memory Agent is running! Type 'exit' to quit.\n")

        # Start empty state and context
        state = {"messages": []}
        context = Context(
            user_id="default",
            model="gpt-4",
            system_prompt="You are a helpful assistant. {user_info}\nTime: {time}",
            thread_id=f"session-{uuid.uuid4()}",  # ✅ unique session ID
        )

        while True:
            user_input = input("You: ")
            if user_input.lower() in {"exit", "quit"}:
                print("👋 Goodbye!")
                break

            # Add user message
            state["messages"].append({"role": "user", "content": user_input})

            # Run the graph ✅ pass thread_id to checkpointer
            state = await graph.ainvoke(
                state,
                config={
                    "configurable": {"thread_id": context.thread_id},
                    "context": context.model_dump(),
                },
            )

            # Print assistant replies
            for msg in state["messages"]:
                if msg.get("role") == "assistant":
                    print(f"Bot: {msg['content']}")

    asyncio.run(chat())
