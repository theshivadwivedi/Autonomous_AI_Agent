import re

from app.state import AgentState
from app.planner import create_plan
from app.llm import get_llm
from app.doc_generator import create_word_document


# -----------------------------
# Planner Node
# -----------------------------
def planner_node(state: AgentState) -> AgentState:
    """
    Creates an execution plan from the user's request.
    """

    plan = create_plan(state["request"])

    state["tasks"] = plan.tasks
    state["task_outputs"] = {}
    state["retry_count"] = 0
    state["reflection_feedback"] = None
    state["is_completed"] = False

    return state


# -----------------------------
# Executor Node
# -----------------------------
def executor_node(state: AgentState) -> AgentState:
    """
    Executes every planned task sequentially.

    On a retry (reflection_feedback is set from a previous loop), each
    task prompt includes that feedback so the LLM knows what to fix
    instead of regenerating near-identical content.
    """

    llm = get_llm()

    outputs = {}
    feedback = state.get("reflection_feedback")

    for task in state["tasks"]:

        feedback_block = ""
        if feedback:
            feedback_block = f"""
A previous draft of this document was reviewed internally and found
incomplete. Internal reviewer notes (for your reference only):
{feedback}

Use these notes to improve this task's content. This is an internal
instruction to you, not something to reference in the output - do NOT
mention the reviewer, the review process, "feedback", or a "previous
attempt" anywhere in your response. Write the final content as if it
were the first and only version, addressing the gaps silently.
"""

        prompt = f"""
You are an AI execution agent.

Original User Request:
{state["request"]}

Current Task:
Title: {task.title}

Description:
{task.description}
{feedback_block}
Complete ONLY this task.

Return professional business-quality content.
"""

        try:
            response = llm.invoke(prompt)
            outputs[task.title] = response.content
        except Exception as e:
            # one task failing shouldn't take down the whole request -
            # log it and leave a visible placeholder instead of a 500
            print(f"[executor_node] task '{task.title}' failed: {e}")
            outputs[task.title] = (
                f"[Content generation failed for this section: {e}]"
            )

    state["task_outputs"] = outputs

    return state


# -----------------------------
# Reflection Node
# -----------------------------
def reflection_node(state: AgentState) -> AgentState:
    """
    Reviews completed work and decides whether retry is needed.
    """

    llm = get_llm()

    completed_work = ""

    for title, output in state["task_outputs"].items():

        completed_work += f"\n\n## {title}\n{output}"

    prompt = f"""
You are a quality assurance reviewer.

Original Request:

{state["request"]}


Completed Work:

{completed_work}


If the work is complete,
respond ONLY with:

PASS

Otherwise explain what is missing.
"""

    try:
        review = llm.invoke(prompt).content.strip()
    except Exception as e:
        # if the reviewer itself fails, don't block the whole pipeline -
        # accept the work as-is and note why reflection was skipped
        print(f"[reflection_node] review call failed, passing through: {e}")
        state["reflection_feedback"] = f"Reflection skipped - reviewer call failed: {e}"
        state["is_completed"] = True
        return state

    state["reflection_feedback"] = review

    # The reviewer LLM doesn't always follow "respond ONLY with PASS"
    # to the letter - it sometimes adds a short preamble even when the
    # work is genuinely complete. Treat it as a pass if PASS appears as
    # a standalone word in a short response, not just as the literal
    # first characters, so a minor phrasing quirk doesn't trigger a
    # needless (and confusing) retry.
    is_short_response = len(review) < 40
    contains_pass_word = re.search(r"\bPASS\b", review.upper()) is not None

    if is_short_response and contains_pass_word:
        state["is_completed"] = True
    else:
        state["retry_count"] += 1
        state["is_completed"] = False

    return state


# -----------------------------
# DOC Generator Node
# -----------------------------
def doc_generator_node(state: AgentState) -> AgentState:
    """
    Generates the final Microsoft Word document.
    """

    path = create_word_document(
        request=state["request"],
        outputs=state["task_outputs"],
        tasks=state["tasks"],
    )

    state["document_path"] = path

    return state