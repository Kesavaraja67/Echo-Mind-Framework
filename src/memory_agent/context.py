from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


def generate_thread_id() -> str:
    """Generate a unique thread/session ID"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    unique_id = uuid.uuid4().hex[:6]  # short random suffix
    return f"session-{timestamp}-{unique_id}"


class Context(BaseModel):
    user_id: str = Field(..., description="Unique user ID")
    model: str = Field(default="gpt-4", description="Which model to use")
    system_prompt: str = Field(
        default="You are a helpful assistant. {user_info}\nTime: {time}",
        description="System prompt template"
    )

    # ✅ Auto-generate a new thread_id for each session
    thread_id: str = Field(
        default_factory=generate_thread_id,
        description="Conversation thread/session ID",
        json_schema_extra={"configurable": True},
    )
