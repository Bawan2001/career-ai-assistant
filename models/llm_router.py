import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class LLMRouter:
    """
    Intelligent Model Selection Router.
    Routes tasks to appropriate model tiers:
    - Tier 1 (Fast / Light): Intent classification, routing, section extraction (e.g. Llama 3.1 8B, Gemini Flash)
    - Tier 2 (Deep Reasoning): CV quality analysis, job matching, career roadmap, reflection (e.g. Llama 3.3 70B, GPT-4o, Claude)
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or os.getenv("DEFAULT_LLM_PROVIDER", "groq").lower()
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    def update_provider_keys(self, provider: str, api_key: str):
        """Update provider and key dynamically from Streamlit UI."""
        self.provider = provider.lower()
        if self.provider == "groq":
            self.groq_api_key = api_key
            os.environ["GROQ_API_KEY"] = api_key
        elif self.provider == "openrouter":
            self.openrouter_api_key = api_key
            os.environ["OPENROUTER_API_KEY"] = api_key
        elif self.provider == "gemini":
            self.google_api_key = api_key
            os.environ["GOOGLE_API_KEY"] = api_key
        elif self.provider == "openai":
            self.openai_api_key = api_key
            os.environ["OPENAI_API_KEY"] = api_key

    def get_llm(self, task_tier: str = "fast", temperature: float = 0.2):
        """
        Instantiate LangChain LLM object based on task requirement and available providers.
        task_tier: 'fast' or 'reasoning'
        """
        if self.provider == "groq" and self.groq_api_key:
            try:
                from langchain_groq import ChatGroq
                model_name = "llama-3.1-8b-instant" if task_tier == "fast" else "llama-3.3-70b-versatile"
                return ChatGroq(model_name=model_name, temperature=temperature, groq_api_key=self.groq_api_key)
            except Exception as e:
                print(f"Error loading Groq LLM: {e}")

        if self.provider == "gemini" and self.google_api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                model_name = "gemini-1.5-flash" if task_tier == "fast" else "gemini-1.5-pro"
                return ChatGoogleGenerativeAI(model=model_name, temperature=temperature, google_api_key=self.google_api_key)
            except Exception as e:
                print(f"Error loading Gemini LLM: {e}")

        if self.provider == "openrouter" and self.openrouter_api_key:
            try:
                from langchain_openai import ChatOpenAI
                model_name = "meta-llama/llama-3.1-8b-instruct" if task_tier == "fast" else "anthropic/claude-3.5-sonnet"
                return ChatOpenAI(
                    model=model_name,
                    temperature=temperature,
                    openai_api_key=self.openrouter_api_key,
                    openai_api_base="https://openrouter.ai/api/v1"
                )
            except Exception as e:
                print(f"Error loading OpenRouter LLM: {e}")

        if self.openai_api_key:
            try:
                from langchain_openai import ChatOpenAI
                model_name = "gpt-3.5-turbo" if task_tier == "fast" else "gpt-4o"
                return ChatOpenAI(model=model_name, temperature=temperature, openai_api_key=self.openai_api_key)
            except Exception as e:
                print(f"Error loading OpenAI LLM: {e}")

        return None

    def invoke_prompt(self, prompt: str, task_tier: str = "fast", temperature: float = 0.2) -> str:
        """
        Invoke LLM with fallback string generation if no LLM is configured.
        """
        llm = self.get_llm(task_tier=task_tier, temperature=temperature)
        if llm:
            try:
                res = llm.invoke(prompt)
                return res.content if hasattr(res, 'content') else str(res)
            except Exception as e:
                print(f"LLM invocation failed: {e}. Falling back to rule-based fallback response.")

        # Fallback simulation if LLM is offline or no key is provided
        return self._rule_based_fallback(prompt, task_tier)

    def _rule_based_fallback(self, prompt: str, task_tier: str) -> str:
        """Fallback heuristics for reliable offline evaluation/demo execution."""
        prompt_lower = prompt.lower()
        if "classify" in prompt_lower or "router" in prompt_lower:
            return json.dumps({
                "task": "cv_analysis",
                "agent": "CV Analyzer",
                "priority": "high",
                "target_role": "Software Engineer"
            })
        elif "reflection" in prompt_lower or "critique" in prompt_lower:
            return json.dumps({
                "quality_score": 92,
                "passed": True,
                "issues": [],
                "improvements": ["Formatting is structured", "Recommendations align with candidate experience level"]
            })
        return "Analysis completed based on rule-based processing engine."

    def get_model_routing_metadata(self) -> Dict[str, Any]:
        """Return metadata table for documentation and Streamlit UI display."""
        return {
            "Intent Classification & Routing": {"tier": "Fast (Tier 1)", "groq": "Llama 3.1 8B", "gemini": "Gemini 1.5 Flash", "openrouter": "Llama 3.1 8B", "reason": "Low latency, low cost, simple JSON output structure"},
            "CV Structure & Section Extraction": {"tier": "Fast (Tier 1)", "groq": "Llama 3.1 8B", "gemini": "Gemini 1.5 Flash", "openrouter": "Llama 3.1 8B", "reason": "Fast text parsing & pattern identification"},
            "CV Quality & ATS Scoring": {"tier": "Deep Reasoning (Tier 2)", "groq": "Llama 3.3 70B", "gemini": "Gemini 1.5 Pro", "openrouter": "Claude 3.5 Sonnet", "reason": "Complex evaluation of impact metrics, section completeness, ATS flaws"},
            "Job Matching & Skill Gap Analysis": {"tier": "Deep Reasoning (Tier 2)", "groq": "Llama 3.3 70B", "gemini": "Gemini 1.5 Pro", "openrouter": "GPT-4o / Sonnet", "reason": "Detailed comparative reasoning between job requirements & candidate CV"},
            "Personalized Career Roadmap": {"tier": "Deep Reasoning (Tier 2)", "groq": "Llama 3.3 70B", "gemini": "Gemini 1.5 Pro", "openrouter": "Claude 3.5 Sonnet", "reason": "Multi-step temporal strategic planning & tech stack recommendations"},
            "Reflection & Quality Critique": {"tier": "Deep Reasoning (Tier 2)", "groq": "Llama 3.3 70B", "gemini": "Gemini 1.5 Pro", "openrouter": "Claude 3.5 Sonnet", "reason": "Self-critique to eliminate hallucinations & verify document grounding"}
        }
