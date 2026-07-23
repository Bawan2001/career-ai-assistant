from typing import Dict, Any
from langgraph.graph import StateGraph, END

from models.llm_router import LLMRouter
from agents.state import AgentState
from agents.router_agent import RouterAgent
from agents.cv_agent import CVAgent
from agents.job_agent import JobMatchingAgent
from agents.career_agent import CareerRecommendationAgent
from agents.rag_agent import RAGKnowledgeAgent
from agents.reflection_agent import ReflectionAgent

class CareerAssistantWorkflow:
    """
    Master Multi-Agent LangGraph Workflow Manager.
    Orchestrates agent-to-agent communication and state propagation.
    """

    def __init__(self, provider: str = "groq"):
        self.llm_router = LLMRouter(provider=provider)
        
        self.router_agent = RouterAgent(self.llm_router)
        self.cv_agent = CVAgent(self.llm_router)
        self.job_agent = JobMatchingAgent(self.llm_router)
        self.career_agent = CareerRecommendationAgent(self.llm_router)
        self.rag_agent = RAGKnowledgeAgent(self.llm_router)
        self.reflection_agent = ReflectionAgent(self.llm_router)

        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)

        # Add Agent Nodes
        workflow.add_node("router", self.router_agent.run)
        workflow.add_node("cv_analysis", self.cv_agent.run)
        workflow.add_node("job_matching", self.job_agent.run)
        workflow.add_node("career_recommendations", self.career_agent.run)
        workflow.add_node("rag_knowledge", self.rag_agent.run)
        workflow.add_node("reflection", self.reflection_agent.run)

        # Set Entry Point
        workflow.set_entry_point("router")

        # Connect Node Edges in Sequential Pipeline
        workflow.add_edge("router", "cv_analysis")
        workflow.add_edge("cv_analysis", "job_matching")
        workflow.add_edge("job_matching", "career_recommendations")
        workflow.add_edge("career_recommendations", "rag_knowledge")
        workflow.add_edge("rag_knowledge", "reflection")
        workflow.add_edge("reflection", END)

        return workflow.compile()

    def run_pipeline(self, user_query: str, raw_cv_text: str = "", job_description: str = "", target_role: str = "") -> Dict[str, Any]:
        """Execute the compiled LangGraph state workflow."""
        initial_state: AgentState = {
            "user_query": user_query,
            "raw_cv_text": raw_cv_text,
            "job_description": job_description,
            "target_role": target_role or "Software Engineer",
            "planner_output": {},
            "cv_analysis_output": {},
            "job_matching_output": {},
            "career_recommendations_output": {},
            "rag_knowledge_output": {},
            "reflection_output": {},
            "active_agent": "Router Agent",
            "execution_logs": [],
            "final_response": ""
        }

        final_state = self.graph.invoke(initial_state)
        return final_state
