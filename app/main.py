from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.graph import graph
from app.schemas import AgentRequest, AgentResponse

templates = Jinja2Templates(directory="app/templates")
app = FastAPI(
    title="Autonomous AI Agent",
    version="1.0.0",
    description="Autonomous planning and document generation agent."
)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )

@app.post("/agent", response_model=AgentResponse)
def run_agent(payload: AgentRequest):

    initial_state = {
        "request": payload.request,
        "tasks": [],
        "task_outputs": {},
        "reflection_feedback": None,
        "is_completed": False,
        "document_path": None,
        "retry_count": 0,
    }

    result = graph.invoke(initial_state)

    return AgentResponse(
        request=result["request"],
        tasks=[task.title for task in result["tasks"]],
        task_outputs=result["task_outputs"],
        reflection_feedback=result["reflection_feedback"],
        document_path=result["document_path"],
    )