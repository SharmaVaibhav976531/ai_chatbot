# backend/app/langgraph/graph.py

from langgraph.graph import StateGraph, END, START
from app.langgraph.state import AgentState
from app.langgraph.nodes import (
    user_input_node, memory_node, planner_node, retriever_node, 
    rag_node, reasoner_node, llm_node, tool_executor_node, 
    response_generator_node, end_node
)

def route_after_planner(state: AgentState) -> str:
    """Determines the next node based on the planner's decision."""
    action = state.get("next_action", "direct")
    if action == "rag":
        return "retriever"
    elif action == "tool":
        return "reasoner" # Go to reasoner to format tool prompt, then LLM
    else:
        return "reasoner"

def route_after_llm(state: AgentState) -> str:
    """Determines if we need to execute tools or finish."""
    if state.get("tool_calls"):
        return "tool_executor"
    return "response_generator"

def build_workflow_graph() -> StateGraph:
    """
    Constructs and compiles the LangGraph workflow.
    The graph is fully configurable and can be extended with new nodes/edges.
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("user_input", user_input_node)
    workflow.add_node("memory", memory_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("reasoner", reasoner_node)
    workflow.add_node("llm", llm_node)
    workflow.add_node("tool_executor", tool_executor_node)
    workflow.add_node("response_generator", response_generator_node)
    workflow.add_node("end", end_node)

    # Define edges
    workflow.add_edge(START, "user_input")
    workflow.add_edge("user_input", "memory")
    workflow.add_edge("memory", "planner")
    
    # Conditional routing after planner
    workflow.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "retriever": "retriever",
            "reasoner": "reasoner"
        }
    )
    
    workflow.add_edge("retriever", "rag")
    workflow.add_edge("rag", "reasoner")
    workflow.add_edge("reasoner", "llm")
    
    # Conditional routing after LLM (Tool execution loop)
    workflow.add_conditional_edges(
        "llm",
        route_after_llm,
        {
            "tool_executor": "tool_executor",
            "response_generator": "response_generator"
        }
    )
    
    workflow.add_edge("tool_executor", "llm") # Loop back to LLM with tool results
    workflow.add_edge("response_generator", "end")
    workflow.add_edge("end", END)

    return workflow.compile()

# Compile the graph once at module load time for performance
compiled_graph = build_workflow_graph()