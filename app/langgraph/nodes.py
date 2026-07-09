# backend/app/langgraph/nodes.py

import json
import structlog
from typing import Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.langgraph.state import AgentState
from app.llms.factory import LLMFactory
from app.vectorstore.factory import VectorStoreFactory
from app.embeddings.factory import EmbeddingsFactory
from app.core.config import settings
from app.services.context import ContextManager

logger = structlog.get_logger()

def user_input_node(state: AgentState) -> dict:
    """Validates and formats the initial user input."""
    messages = state["messages"]
    if not messages or not isinstance(messages[-1], HumanMessage):
        raise ValueError("The last message must be a HumanMessage")
    
    logger.info("user_input_processed", chat_id=state["chat_id"])
    return {"messages": []} # No state mutation needed, just validation

def memory_node(state: AgentState) -> dict:
    """
    Loads conversation history and injects it into the context.
    In a full implementation, this would fetch from the DB. 
    Here, we rely on the messages already passed in the state from the API layer.
    """
    logger.info("memory_loaded", chat_id=state["chat_id"], msg_count=len(state["messages"]))
    return {"messages": []}

def planner_node(state: AgentState) -> dict:
    """
    Analyzes the user query and decides the next action:
    - 'direct': Simple conversational response.
    - 'rag': Requires external knowledge retrieval.
    - 'tool': Requires executing a tool (e.g., calculator, search).
    """
    last_message = state["messages"][-1].content.lower()
    
    # Simple heuristic routing for demonstration. 
    # In production, this would be an LLM call or a more complex classifier.
    if any(keyword in last_message for keyword in ["calculate", "math", "sum", "multiply"]):
        next_action = "tool"
    elif any(keyword in last_message for keyword in ["document", "file", "pdf", "context", "what does the document say"]):
        next_action = "rag"
    else:
        next_action = "direct"
        
    logger.info("planner_routed", chat_id=state["chat_id"], action=next_action)
    return {"next_action": next_action}

def retriever_node(state: AgentState) -> dict:
    """Fetches relevant documents from the Vector Database."""
    query = state["messages"][-1].content
    embeddings = EmbeddingsFactory.get_embeddings(settings.EMBEDDINGS_PROVIDER, settings.EMBEDDINGS_MODEL)
    vectorstore = VectorStoreFactory.get_vector_store()
    
    # Run embedding and search in a synchronous wrapper for the node
    import asyncio
    loop = asyncio.new_event_loop()
    try:
        query_embedding = loop.run_until_complete(embeddings.embed_query(query))
        results = loop.run_until_complete(
            vectorstore.search(query_embedding, top_k=3, filter={"user_id": state["user_id"]})
        )
    finally:
        loop.close()
        
    context = "\n\n".join([res["content"] for res in results])
    logger.info("documents_retrieved", chat_id=state["chat_id"], count=len(results))
    return {"retrieved_context": context}

def rag_node(state: AgentState) -> dict:
    """Compresses and formats the retrieved context for the LLM."""
    context = state.get("retrieved_context", "")
    if not context:
        return {"retrieved_context": "No relevant documents found."}
    
    # Context compression/formatting
    formatted_context = f"--- Retrieved Context ---\n{context}\n-------------------------"
    return {"retrieved_context": formatted_context}

def reasoner_node(state: AgentState) -> dict:
    """Synthesizes the state into a structured prompt for the LLM."""
    messages = state["messages"]
    next_action = state["next_action"]
    
    system_prompt = "You are a helpful AI assistant."
    
    if next_action == "rag":
        system_prompt += f"\n\nUse the following context to answer the user's question:\n{state['retrieved_context']}"
    elif next_action == "tool":
        system_prompt += "\n\nYou have access to tools. If you need to use a tool, respond with a JSON object containing 'tool_calls'."
        
    # Inject system prompt at the beginning of the message list
    if not messages or not isinstance(messages[0], SystemMessage):
        messages.insert(0, SystemMessage(content=system_prompt))
    else:
        messages[0].content = system_prompt
        
    return {"messages": messages}

def llm_node(state: AgentState) -> dict:
    """Calls the configured LLM provider."""
    messages = state["messages"]
    provider = state["provider"]
    model = state["model"]
    
    # Convert LangChain messages to our LLM format
    formatted_msgs = [{"role": m.type if m.type != "human" else "user", "content": m.content} for m in messages]
    # Fix role mapping
    for m in formatted_msgs:
        if m["role"] == "human": m["role"] = "user"
        elif m["role"] == "ai": m["role"] = "assistant"
        elif m["role"] == "system": m["role"] = "system"

    llm = LLMFactory.get_llm(provider, model)
    
    import asyncio
    loop = asyncio.new_event_loop()
    try:
        response_text = loop.run_until_complete(llm.complete(formatted_msgs))
    finally:
        loop.close()
        
    # Check for tool calls (simple JSON parsing for demonstration)
    tool_calls = []
    if state["next_action"] == "tool" and response_text.strip().startswith("{"):
        try:
            parsed = json.loads(response_text)
            if "tool_calls" in parsed:
                tool_calls = parsed["tool_calls"]
        except json.JSONDecodeError:
            pass

    logger.info("llm_generated", chat_id=state["chat_id"], has_tool_calls=bool(tool_calls))
    return {
        "messages": [AIMessage(content=response_text)],
        "tool_calls": tool_calls,
        "final_response": response_text
    }

def tool_executor_node(state: AgentState) -> dict:
    """Executes requested tools and feeds the result back to the LLM."""
    tool_calls = state.get("tool_calls", [])
    results = []
    
    for call in tool_calls:
        tool_name = call.get("name")
        args = call.get("args", {})
        
        if tool_name == "calculator":
            try:
                # Safe evaluation for basic math
                result = eval(args.get("expression", "0"), {"__builtins__": {}}, {})
                results.append(f"Tool '{tool_name}' result: {result}")
            except Exception as e:
                results.append(f"Tool '{tool_name}' error: {str(e)}")
        else:
            results.append(f"Tool '{tool_name}' not found.")
            
    tool_output = "\n".join(results)
    logger.info("tools_executed", chat_id=state["chat_id"], tools=[c.get("name") for c in tool_calls])
    
    return {
        "messages": [AIMessage(content=f"Tool execution results:\n{tool_output}\n\nPlease summarize this for the user.")],
        "tool_calls": [] # Clear tool calls after execution
    }

def response_generator_node(state: AgentState) -> dict:
    """Formats the final response for the user."""
    final_response = state.get("final_response", "I'm sorry, I couldn't generate a response.")
    logger.info("response_generated", chat_id=state["chat_id"])
    return {"final_response": final_response}

def end_node(state: AgentState) -> dict:
    """Cleans up the state and prepares for termination."""
    logger.info("workflow_ended", chat_id=state["chat_id"])
    return {}