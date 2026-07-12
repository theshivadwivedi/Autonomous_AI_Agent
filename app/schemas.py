from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """
    Incoming API request.
    """

    request: str = Field(
        ...,
        min_length=10,
        description="Natural language request for the autonomous agent."
    )


class AgentResponse(BaseModel):
    """
    API response returned after graph execution.
    """

    request: str

    tasks: list[str]

    task_outputs: dict[str, str]

    reflection_feedback: str

    document_path: str