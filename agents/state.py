from typing import TypedDict, Dict, Any, List, Optional

class AgentState(TypedDict):
    """
    LangGraph State Schema holding structured inter-agent messages,
    artifacts, and execution step data.
    """
    user_query: str
    raw_cv_text: str
    job_description: str
    target_role: str
    
    # Inter-agent JSON messages
    planner_output: Dict[str, Any]
    cv_analysis_output: Dict[str, Any]
    job_matching_output: Dict[str, Any]
    career_recommendations_output: Dict[str, Any]
    rag_knowledge_output: Dict[str, Any]
    reflection_output: Dict[str, Any]
    
    # Execution status
    active_agent: str
    execution_logs: List[Dict[str, Any]]
    final_response: str
