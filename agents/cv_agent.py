import json
from typing import Dict, Any
from models.llm_router import LLMRouter
from tools.cv_parser import CVParser
from tools.resume_analyzer import ResumeAnalyzer
from agents.state import AgentState

class CVAgent:
    """
    AGENT 2: CV Analysis Agent
    Design Pattern: Tool Usage Pattern
    
    Responsibilities:
    - Extract Education, Skills, Experience, Certifications
    - Calculate ATS quality score & section breakdown
    - Highlight formatting weaknesses and missing keywords
    - Provide improvement suggestions
    """

    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router

    def run(self, state: AgentState) -> Dict[str, Any]:
        raw_cv_text = state.get("raw_cv_text", "")
        
        if not raw_cv_text:
            return {
                "cv_analysis_output": {
                    "status": "error",
                    "score": 0,
                    "issues": ["No CV content uploaded"],
                    "summary": "Please upload a valid PDF CV to perform analysis."
                }
            }

        # 1. Use Tool: Parse structured sections
        structured_cv = CVParser.parse_structured_cv(raw_cv_text)
        
        # 2. Use Tool: Calculate ATS Score & Quantitative Metrics
        ats_result = ResumeAnalyzer.calculate_ats_score(structured_cv)

        # 3. LLM Deep Reasoning for qualitative improvements
        prompt = f"""
You are the CV Analysis Agent. Perform a deep qualitative analysis of the candidate's CV.

CV Text:
\"\"\"
{raw_cv_text[:3000]}
\"\"\"

ATS Quantitative Score: {ats_result['overall_score']}/100
Quantitative Flaws Identified: {ats_result['flaws']}

Provide qualitative evaluation in valid JSON:
{{
    "status": "complete",
    "score": {ats_result['overall_score']},
    "strengths": ["Strength 1...", "Strength 2..."],
    "weaknesses": ["Weakness 1...", "Weakness 2..."],
    "actionable_improvements": ["Improvement 1...", "Improvement 2..."],
    "summary_eval": "Executive summary paragraph of candidate profile quality."
}}
"""
        response_text = self.llm_router.invoke_prompt(prompt, task_tier="reasoning")

        try:
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            llm_eval = json.loads(clean_text)
        except Exception:
            llm_eval = {
                "status": "complete",
                "score": ats_result['overall_score'],
                "strengths": [f"Detected {len(ats_result['detected_skills'])} tech skills", "Includes professional history"],
                "weaknesses": ats_result['flaws'],
                "actionable_improvements": [
                    "Add measurable impact metrics (% efficiency gains, revenue saved, user scale)",
                    "Include strong technical action verbs at start of bullet points",
                    "Add targeted technical keywords for ATS compatibility"
                ],
                "summary_eval": "Candidate possesses foundational skills but needs ATS optimization and metric-driven impact statements."
            }

        # Combine quantitative & qualitative results
        combined_output = {
            **llm_eval,
            "ats_breakdown": ats_result['breakdown'],
            "detected_skills": ats_result['detected_skills'],
            "action_verbs_found": ats_result['action_verbs_found'],
            "structured_sections": {
                "contact": structured_cv["contact_info"],
                "has_skills": bool(structured_cv["skills"]),
                "has_experience": bool(structured_cv["experience"]),
                "has_education": bool(structured_cv["education"]),
                "has_projects": bool(structured_cv["projects"]),
                "has_certifications": bool(structured_cv["certifications"])
            }
        }

        # Inter-agent status communication
        inter_agent_msg = {
            "sender": "CV Analysis Agent",
            "recipient": "Job Matching / Career Agent",
            "status": "complete",
            "score": ats_result['overall_score'],
            "issues": llm_eval.get("weaknesses", [])
        }

        logs = state.get("execution_logs", [])
        logs.append(inter_agent_msg)

        return {
            "cv_analysis_output": combined_output,
            "execution_logs": logs
        }
