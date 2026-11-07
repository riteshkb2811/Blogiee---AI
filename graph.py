from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt,Command

from state import BlogState
from agent import writer_agent,researcher_agent,final_draft

MAX_REVISION=3

def researcher_node(state:BlogState):
    """
    Generates the research outline and updates the state.
    """
    feedback = state.research_state
    result = researcher_agent(state, feedback)    
    return {
        "research": result["research"],
        "research_state": feedback
    }


     
def writer_node(state:BlogState):
    """
    Generates the draft and updates the state.
    """
    feedback = state.draft_state
    result = writer_agent(state, feedback)    
    return {
        "draft": result["draft"],
        "draft_state": feedback
    }
def final_draft_node(state:BlogState):
    """
    Generates the final draft and give it to user 
    """
    result = final_draft(state)    
    return {
        "final_draft": result["final_draft"],
    }


def human_research_review_node(state: BlogState):
    """
    Pauses execution and sends the research outline to the human for review.
    Resumes when the human provides approval or feedback.
    """
    human_response = interrupt({
        "question": "Please review this research outline.",
        "research": state.research
    })
    
    # If the human gives revision notes/feedback
    if human_response.get("feedback"):
        return {
            "research_state": human_response["feedback"],
            "revision_count": state.revision_count + 1
        }
    
    # If approved
    return {
        "research_state": "approved"
    }



def route_after_research(state: BlogState):
    if state.research_state == "approved" or state.revision_count >= MAX_REVISION:
        state.revision_count=0
        return "writer"
    return "researcher"



def human_draft_review_node(state: BlogState):
    human_response = interrupt({
        "question": "Please review this draft.",
        "draft": state.draft
    })
    if human_response.get("feedback"):
        return {
            "draft_state": human_response["feedback"],
            "revision_count": state.revision_count + 1
        }
    return {"draft_state": "approved"}



def route_after_draft(state: BlogState):
    if state.draft_state == "approved" or state.revision_count >= MAX_REVISION:
        return "final_draft"
    return "writer"




blog = StateGraph(BlogState)
blog.add_node("researcher", researcher_node)
blog.add_node("hilp_research",human_research_review_node)
blog.add_node("writer", writer_node)
blog.add_node("hilp_draft", human_draft_review_node)
blog.add_node("final_draft", final_draft_node)
blog.add_edge(START, "researcher")
blog.add_edge("researcher", "hilp_research")
blog.add_conditional_edges("hilp_research", route_after_research, {
    "researcher": "researcher",
    "writer": "writer"
})
blog.add_edge("writer", "hilp_draft")
blog.add_conditional_edges("hilp_draft", route_after_draft, {
    "writer": "writer",
    "final_draft": "final_draft"
})
blog.add_edge("final_draft", END)


checkpointer = InMemorySaver()
app = blog.compile(checkpointer=checkpointer)


