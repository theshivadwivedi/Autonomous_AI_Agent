from typing import TypedDict
from pydantic import BaseModel
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class Task(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.PENDING

class Plan(BaseModel):
    tasks: list[Task]

class AgentState(TypedDict):
    request: str
    tasks: list[Task]
    task_outputs: dict[str, str]
    reflection_feedback: str | None
    is_completed: bool
    document_path: str | None 
    retry_count: int

