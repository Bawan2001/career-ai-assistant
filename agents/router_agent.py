import json
from typing import Dict, Any
from models.llm_router import LLMRouter
from agents.state import AgentState

class RouterAgent:
    """
    AGENT 1: Router / Planner Agent
    Design Pattern: Planning Pattern
    
    Responsibilities:
    - Classify user request intent
    - Select execution workflow and required specialized agents
    - Generate structured JSON task plan
    """

    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router

    def run(self, state: AgentState) -> Dict[str, Any]:
        user_query = state.get("user_query", "")
        raw_cv = state.get("raw_cv_text", "")
        job_desc = state.get("job_description", "")

        prompt = f"""
You are the Router/Planner Agent in an Agentic AI system for Career Guidance and CV Improvement.
Analyze the user request and available inputs:

User Query: "{user_query}"
CV Provided: {"Yes" if len(raw_cv) > 50 else "No"}
Job Description Provided: {"Yes" if len(job_desc) > 50 else "No"}

Classify the intent into one of the primary workflows:
1. "cv_analysis": User wants CV parsed, ATS scored, and weaknesses highlighted.
2. "job_matching": User wants CV compared against a target Job Description.
3. "career_recommendations": User wants career advice, learning roadmaps, and role suggestions.
4. "rag_qa": User is asking a career, ATS, technical skill, or interview question.
5. "full_pipeline": Execute complete end-to-end evaluation.

Return ONLY a valid JSON object matching this structure:
{{
    "task": "<classified_workflow>",
    "agent": "<Primary_Agent_Name>",
    "priority": "high",
    "target_role": "<Inferred_or_specified_target_role>",
    "steps": ["Step 1...", "Step 2..."]
}}
"""
        response_text = self.llm_router.invoke_prompt(prompt, task_tier="fast")
        
        try:
            # Extract JSON from potential Markdown code blocks
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            plan_json = json.loads(clean_text)
        except Exception:
            # Safe JSON fallback
            task_type = "cv_analysis" if len(raw_cv) > 50 else "rag_qa"
            if len(job_desc) > 50:
                task_type = "job_matching"
            plan_json = {
                "task": task_type,
                "agent": "CV Analyzer" if task_type == "cv_analysis" else "RAG Knowledge Agent",
                "priority": "high",
                "target_role": state.get("target_role", "Software Engineer"),
                "steps": ["Parse CV", "Analyze ATS Score", "Formulate Recommendations"]
            }

        # Format inter-agent communication message
        inter_agent_msg = {
            "sender": "Planner Agent",
            "recipient": plan_json.get("agent", "CV Analyzer"),
            "action": "execute_task",
            "json_payload": plan_json
        }

        logs = state.get("execution_logs", [])
        logs.append(inter_agent_msg)

        return {
            "planner_output": plan_json,
            "execution_logs": logs,
            "active_agent": plan_json.get("agent", "CV Analyzer")
        }
