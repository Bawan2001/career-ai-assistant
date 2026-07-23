import re
from typing import Dict, Any, List

class ResumeAnalyzer:
    """
    ATS scoring and quantitative resume quality analyzer.
    """

    ACTION_VERBS = [
        "developed", "designed", "architected", "implemented", "managed", "led",
        "built", "created", "optimized", "spearheaded", "engineered", "integrated",
        "automated", "reduced", "increased", "improved", "launched", "deployed"
    ]

    TECH_SKILLS_DICTIONARY = [
        "python", "java", "c++", "javascript", "typescript", "html", "css", "sql", "nosql",
        "react", "angular", "vue", "node.js", "express", "django", "flask", "fastapi", "spring boot",
        "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "ci/cd", "git", "github",
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "langchain", "langgraph",
        "faiss", "chromadb", "rag", "rest api", "graphql", "microservices", "mongodb", "postgresql"
    ]

    @staticmethod
    def calculate_ats_score(structured_cv: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates comprehensive ATS Score (0 - 100) based on multiple factors:
        1. Section Completeness (30%)
        2. Action Verbs & Impact Keywords (20%)
        3. Technical Skills Density (30%)
        4. Contact Info Completeness (10%)
        5. Quantifiable Achievements (10%)
        """
        raw_text = structured_cv.get("raw_text", "")
        raw_text_lower = raw_text.lower()

        # 1. Section Completeness (30 pts)
        sections = ["skills", "experience", "education", "projects", "summary"]
        present_sections = [s for s in sections if structured_cv.get(s) or s in raw_text_lower]
        section_score = (len(present_sections) / len(sections)) * 30

        # 2. Action Verbs (20 pts)
        found_verbs = [v for v in ResumeAnalyzer.ACTION_VERBS if re.search(rf'\b{v}\b', raw_text_lower)]
        verb_score = min(len(found_verbs) * 2.5, 20.0)

        # 3. Technical Skills (30 pts)
        found_skills = [s for s in ResumeAnalyzer.TECH_SKILLS_DICTIONARY if re.search(rf'\b{re.escape(s)}\b', raw_text_lower)]
        skill_score = min(len(found_skills) * 3.0, 30.0)

        # 4. Contact Info (10 pts)
        contact = structured_cv.get("contact_info", {})
        contact_items = [v for v in contact.values() if v != "Not found"]
        contact_score = min(len(contact_items) * 2.5, 10.0)

        # 5. Quantifiable Achievements (10 pts - checking for numbers/percentages)
        metrics_matches = re.findall(r'\b\d+(?:%|\+|\s*k|\s*million|\s*users|\s*hrs|\s*percent)?\b', raw_text)
        metrics_score = min(len(metrics_matches) * 2.0, 10.0)

        total_score = round(section_score + verb_score + skill_score + contact_score + metrics_score, 1)

        # Identify key flaws and recommendations
        flaws = []
        if len(present_sections) < len(sections):
            missing = set(sections) - set(present_sections)
            flaws.append(f"Missing core sections: {', '.join(missing).title()}")

        if len(found_verbs) < 5:
            flaws.append("Low density of strong action verbs (e.g. Architected, Optimized, Spearheaded)")

        if len(found_skills) < 6:
            flaws.append("Limited technical keywords detected for ATS filtering")

        if metrics_score < 4.0:
            flaws.append("Few quantifiable metrics or numerical achievements (% improvement, user scale, cost savings)")

        if contact.get("linkedin") == "Not found":
            flaws.append("Missing LinkedIn profile link")

        return {
            "overall_score": total_score,
            "breakdown": {
                "section_completeness": round(section_score, 1),
                "action_verbs": round(verb_score, 1),
                "technical_skills": round(skill_score, 1),
                "contact_info": round(contact_score, 1),
                "quantifiable_metrics": round(metrics_score, 1)
            },
            "detected_skills": sorted(list(set(found_skills))),
            "action_verbs_found": sorted(list(set(found_verbs))),
            "flaws": flaws
        }

    @staticmethod
    def compare_cv_with_job(cv_text: str, job_description: str) -> Dict[str, Any]:
        """
        Compares CV raw text against a target Job Description.
        Calculates skill match percentage and missing keywords.
        """
        cv_lower = cv_text.lower()
        jd_lower = job_description.lower()

        # Extract tech keywords present in JD
        jd_skills = [s for s in ResumeAnalyzer.TECH_SKILLS_DICTIONARY if re.search(rf'\b{re.escape(s)}\b', jd_lower)]

        if not jd_skills:
            # Fallback keyword extraction from JD using frequency
            words = re.findall(r'\b[a-zA-Z]{3,15}\b', jd_lower)
            from collections import Counter
            common = [w for w, _ in Counter(words).most_common(15) if w not in ["the", "and", "for", "with", "that", "this", "will", "are", "have", "you", "your"]]
            jd_skills = common[:10]

        matched_skills = [s for s in jd_skills if re.search(rf'\b{re.escape(s)}\b', cv_lower)]
        missing_skills = list(set(jd_skills) - set(matched_skills))

        match_pct = round((len(matched_skills) / max(len(jd_skills), 1)) * 100, 1)

        return {
            "match_percentage": match_pct,
            "matched_skills": sorted(matched_skills),
            "missing_skills": sorted(missing_skills),
            "target_skills_required": sorted(jd_skills)
        }
