from app.llm import get_llm
from app.prompts import planner_prompt
from app.state import Plan

def create_plan(request: str) -> Plan:
    """
    Generate an execution plan from the user request.
    """
    planner = planner_prompt | get_llm().with_structured_output(Plan)

    plan = planner.invoke (
        {
            "request" : request
        }
    )

    return plan
