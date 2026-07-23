import json
from typing import Dict, Any
from models.llm_router import LLMRouter
from tools.resume_analyzer import ResumeAnalyzer
from agents.state import AgentState

class JobMatchingAgent:
    """
    AGENT 3: Job Matching Agent
    Design Pattern: Comparative Tool & Reasoning Pattern
    
    Responsibilities:
    - Compare candidate CV against target Job Description
    - Calculate skill match percentage
    - Identify missing required & optional technical skills
    - Generate comprehensive Skill Gap Report
    """

    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router

    def run(self, state: AgentState) -> Dict[str, Any]:
        raw_cv = state.get("raw_cv_text", "")
        job_desc = state.get("job_description", "")

        if not job_desc or not raw_cv:
            return {
                "job_matching_output": {
                    "status": "error",
                    "match_percentage": 0,
                    "summary": "Both CV and Job Description are required for Job Matching analysis."
                }
            }

        # 1. Tool execution: Extract skill comparison statistics
        comparison = ResumeAnalyzer.compare_cv_with_job(raw_cv, job_desc)

        # 2. LLM Deep Reasoning for detailed gap analysis
        prompt = f"""
You are the Job Matching Agent. Compare this Candidate CV with the Target Job Description.

CV Text Snippet:
\"\"\"
{raw_cv[:2500]}
\"\"\"

Job Description:
\"\"\"
{job_desc[:2500]}
\"\"\"

Statistical Keyword Match Percentage: {comparison['match_percentage']}%
Matched Skills: {comparison['matched_skills']}
Missing Target Skills: {comparison['missing_skills']}

Provide detailed JSON evaluation:
{{
    "status": "complete",
    "match_percentage": {comparison['match_percentage']},
    "role_alignment_level": "High/Medium/Low",
    "key_matched_skills": {comparison['matched_skills']},
    "critical_missing_skills": {comparison['missing_skills']},
    "experience_alignment_notes": "Evaluation of whether experience level matches job expectations.",
    "recommendations_to_pass_screening": ["Step 1...", "Step 2..."]
}}
"""
        response_text = self.llm_router.invoke_prompt(prompt, task_tier="reasoning")

        try:
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            llm_matching = json.loads(clean_text)
        except Exception:
            alignment = "High" if comparison['match_percentage'] >= 70 else ("Medium" if comparison['match_percentage'] >= 45 else "Low")
            llm_matching = {
                "status": "complete",
                "match_percentage": comparison['match_percentage'],
                "role_alignment_level": alignment,
                "key_matched_skills": comparison['matched_skills'],
                "critical_missing_skills": comparison['missing_skills'],
                "experience_alignment_notes": f"Candidate matches {comparison['match_percentage']}% of key technical terms required in the job description.",
                "recommendations_to_pass_screening": [
                    "Highlight missing key skills in project bullet points",
                    "Tailor professional summary to emphasize job description priorities",
                    "Add domain-specific frameworks mentioned in the posting"
                ]
            }

        # Inter-agent status communication
        inter_agent_msg = {
            "sender": "Job Matching Agent",
            "recipient": "Career Recommendation Agent",
            "status": "complete",
            "match_percentage": comparison['match_percentage'],
            "missing_skills_count": len(comparison['missing_skills'])
        }

        logs = state.get("execution_logs", [])
        logs.append(inter_agent_msg)

        return {
            "job_matching_output": llm_matching,
            "execution_logs": logs
        }
