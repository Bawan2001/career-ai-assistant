import json
from typing import Dict, Any
from models.llm_router import LLMRouter
from agents.state import AgentState

class CareerRecommendationAgent:
    """
    AGENT 4: Career Recommendation Agent
    Design Pattern: Strategic Planning & Guidance Pattern
    
    Responsibilities:
    - Recommend suitable target job roles based on candidate skills
    - Generate personalized 4 to 8 week learning roadmap
    - Suggest high-value tech stack & certification recommendations
    - Formulate actionable career advancement strategy
    """

    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router

    def run(self, state: AgentState) -> Dict[str, Any]:
        cv_analysis = state.get("cv_analysis_output", {})
        job_match = state.get("job_matching_output", {})
        raw_cv = state.get("raw_cv_text", "")

        detected_skills = cv_analysis.get("detected_skills", [])
        missing_skills = job_match.get("critical_missing_skills", [])

        prompt = f"""
You are the Career Recommendation Agent. Provide strategic career guidance for the candidate.

Candidate CV Overview:
Detected Skills: {detected_skills}
Target Job Gap Skills: {missing_skills}
CV ATS Score: {cv_analysis.get("score", 70)}/100

Generate a comprehensive JSON guidance plan:
{{
    "status": "complete",
    "suitable_job_roles": [
        {{"role": "Role Title 1", "fit_reason": "Why candidate is suitable"}},
        {{"role": "Role Title 2", "fit_reason": "Why candidate is suitable"}}
    ],
    "learning_roadmap": [
        {{"phase": "Weeks 1-2: Core Foundations", "focus": "Topics to learn", "action_items": ["Task 1", "Task 2"]}},
        {{"phase": "Weeks 3-4: Hands-on Projects", "focus": "Topics to build", "action_items": ["Project 1", "Project 2"]}},
        {{"phase": "Weeks 5-8: Advanced Integration", "focus": "System design & portfolio", "action_items": ["Deployment", "ATS Optimization"]}}
    ],
    "recommended_certifications": ["Cert 1", "Cert 2"],
    "recommended_tech_stack": ["Tech 1", "Tech 2", "Tech 3"],
    "portfolio_project_ideas": ["Project Idea 1 with description", "Project Idea 2 with description"]
}}
"""
        response_text = self.llm_router.invoke_prompt(prompt, task_tier="reasoning")

        try:
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            recs_json = json.loads(clean_text)
        except Exception:
            recs_json = {
                "status": "complete",
                "suitable_job_roles": [
                    {"role": "Junior / Mid Software Engineer", "fit_reason": "Matches foundational programming and problem-solving skills."},
                    {"role": "Full Stack / AI Solutions Developer", "fit_reason": "Aligns with Python, Web development, and AI interest."}
                ],
                "learning_roadmap": [
                    {
                        "phase": "Weeks 1-2: Core Technical Bridge",
                        "focus": "Master missing foundational skills and frameworks",
                        "action_items": ["Complete interactive tutorials on missing skills", "Build small prototype APIs"]
                    },
                    {
                        "phase": "Weeks 3-4: Portfolio Execution",
                        "focus": "Build end-to-end deployed capstone project",
                        "action_items": ["Architect RAG or microservice web app", "Deploy on cloud (Vercel/AWS)"]
                    },
                    {
                        "phase": "Weeks 5-8: ATS & Interview Polish",
                        "focus": "Optimize CV bullet points & technical interview prep",
                        "action_items": ["Refactor CV with metric outcomes", "Practice 25 LeetCode medium questions"]
                    }
                ],
                "recommended_certifications": ["AWS Certified Solutions Architect", "TensorFlow / Databricks Developer"],
                "recommended_tech_stack": ["FastAPI", "Docker", "LangChain", "PostgreSQL", "React"],
                "portfolio_project_ideas": [
                    "Multi-Agent AI Workflow Application with LangGraph and Streamlit UI",
                    "High-Throughput Microservice API with Caching and Docker Containerization"
                ]
            }

        # Inter-agent status communication
        inter_agent_msg = {
            "sender": "Career Recommendation Agent",
            "recipient": "Reflection Agent",
            "status": "complete",
            "recommended_roles_count": len(recs_json.get("suitable_job_roles", []))
        }

        logs = state.get("execution_logs", [])
        logs.append(inter_agent_msg)

        return {
            "career_recommendations_output": recs_json,
            "execution_logs": logs
        }
