from langgraph.graph import StateGraph, START, END
from app.state import AgentState

from app.nodes import(
    planner_node,
    executor_node,
    reflection_node,
    doc_generator_node,
)

MAX_RETRIES = 2

def reflection_router(state: AgentState)-> str:
    """
     Decide the next step after reflection.

    Returns:
        "doc_generator" -> if reflection passes, OR we've already retried
                            the max number of times (avoid infinite loop)
        "executor" -> if retry is required and we have retries left
    """

    if state["is_completed"]:
        return "doc_generator"

    if state["retry_count"] >= MAX_RETRIES:
       
        return "doc_generator"

    return "executor"

builder = StateGraph(AgentState)

builder.add_node("planner", planner_node)

builder.add_node("executor", executor_node)

builder.add_node("reflection", reflection_node)

builder.add_node("doc_generator", doc_generator_node)

builder.add_edge(START, "planner")

builder.add_edge("planner", "executor")

builder.add_edge("executor", "reflection")

builder.add_conditional_edges(
    "reflection",
    reflection_router,
)

builder.add_edge("doc_generator", END)

graph = builder.compile()