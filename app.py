import os
import json
import streamlit as st
import pandas as pd

# Load Streamlit Cloud secrets into environment variables if available
try:
    if hasattr(st, 'secrets'):
        for key in ["GROQ_API_KEY", "OPENROUTER_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY", "DEFAULT_LLM_PROVIDER"]:
            if key in st.secrets:
                os.environ[key] = st.secrets[key]
except Exception:
    pass

from models.llm_router import LLMRouter
from tools.cv_parser import CVParser
from agents.workflow import CareerAssistantWorkflow
from frontend.components.styles import apply_custom_css
from frontend.components.charts import (
    create_ats_score_gauge,
    create_ats_breakdown_chart,
    create_skill_gap_chart
)
from utils.export_pdf import generate_pdf_report

# Page Configuration (must be the first Streamlit command)
st.set_page_config(
    page_title="AI Career Guidance & CV Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# FAISS Cold-Start: Ensure vector database is initialized on first run
@st.cache_resource(show_spinner="Building knowledge base (first run only)...")
def initialize_faiss():
    """Build FAISS index on first application launch if not already persisted."""
    try:
        from rag.vector_store import FAISSVectorStoreManager
        manager = FAISSVectorStoreManager()
        manager.initialize_vector_store()
        return True
    except Exception as e:
        st.warning(f"RAG knowledge base initialization warning: {e}. Chat features may use fallback mode.")
        return False

initialize_faiss()

# Apply Modern Custom CSS
apply_custom_css()

# Session State Initialization
if "raw_cv_text" not in st.session_state:
    st.session_state.raw_cv_text = ""
if "job_description" not in st.session_state:
    st.session_state.job_description = ""
if "target_role" not in st.session_state:
    st.session_state.target_role = "Software Engineer"
if "pipeline_results" not in st.session_state:
    st.session_state.pipeline_results = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = "groq"
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# Sidebar - Settings & Model Router Configuration
with st.sidebar:
    st.image("https://img.icons8.com/isometric-folders/100/brain.png", width=64)
    st.title("🤖 System Configuration")
    
    st.markdown("### Horizon Campus IT41043")
    st.caption("Intelligent Systems - Agentic AI Project")
    
    st.divider()
    
    st.subheader("⚙️ Multi-Model LLM Router")
    provider_choice = st.selectbox(
        "Select LLM Provider",
        ["Groq", "OpenRouter", "Google Gemini", "OpenAI"],
        index=0
    )

    api_key_input = st.text_input(
        f"{provider_choice} API Key",
        type="password",
        value=st.session_state.api_key,
        help="Enter active API Key to enable live LLM execution."
    )

    if api_key_input:
        st.session_state.api_key = api_key_input

    st.session_state.llm_provider = provider_choice.lower()
    
    st.info("💡 **Model Routing Strategy**\n\n- **Fast Tier (Llama 3.1 8B / Flash)**: Intent Routing & Parsing\n- **Deep Tier (Llama 3.3 70B / Sonnet / GPT-4o)**: CV Analysis, Gap Analysis & Reflection")

    st.divider()
    st.caption("Built with LangGraph, Streamlit, FAISS & Sentence-Transformers.")

# Instantiate Multi-Agent Workflow
workflow = CareerAssistantWorkflow(provider=st.session_state.llm_provider)
if st.session_state.api_key:
    workflow.llm_router.update_provider_keys(st.session_state.llm_provider, st.session_state.api_key)

# Main Header Banner
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🎓 AI Career Guidance & CV Improvement Assistant</div>
    <div class="hero-subtitle">
        Multi-Agent RAG Architecture powering intelligent CV analysis, skill gap detection, personalized learning roadmaps, and grounded career Q&A.
    </div>
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs
tabs = st.tabs([
    "🏠 Home",
    "📄 Upload CV",
    "📊 CV Analysis",
    "🎯 Job Matching",
    "🚀 Career Recommendations",
    "💬 AI Career Chat",
    "📥 Reports & Logs"
])

# ---------------------------------------------------------
# TAB 1: HOME
# ---------------------------------------------------------
with tabs[0]:
    st.header("📌 Project Architecture & Design Patterns")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("System Architecture")
        st.markdown("""
        ```
        User (Streamlit Interface)
                   ↓
        Router / Planner Agent (Planning Pattern)
                   ↓
        -------------------------------------------------------------
        | CV Analysis | Job Matching | Career Recs | RAG Knowledge |
        -------------------------------------------------------------
                   ↓
        Reflection / Quality Control Agent (Reflection Pattern)
                   ↓
        Final Interactive Response & Visual Dashboard
        ```
        """)
        
        st.subheader("Key Agentic Design Patterns")
        st.markdown("""
        1. **Planning Pattern**: Router Agent evaluates query intent and formulates structured JSON task workflow.
        2. **Tool Usage Pattern**: CV Agent and RAG Agent employ PDF Parsers, ATS Calculators, and FAISS Vector Retrievers.
        3. **Reflection Pattern**: Reflection Agent audits outputs for hallucinations, missing details, and recommendations quality.
        4. **Multi-Model Router Pattern**: Automatically routes simple extraction tasks to fast LLMs and complex reasoning to deep LLMs.
        """)

    with col2:
        st.subheader("Model Selection Table")
        router_meta = workflow.llm_router.get_model_routing_metadata()
        meta_df = pd.DataFrame.from_dict(router_meta, orient='index')
        st.dataframe(meta_df[["tier", "groq", "reason"]], use_container_width=True)

        st.subheader("⚡ Quick Start")
        st.markdown("""
        1. Go to **Upload CV** tab to upload your resume PDF.
        2. Paste a target job description under **Job Matching**.
        3. Click **Run Multi-Agent Pipeline** to trigger all 6 agents.
        4. Explore analysis, roadmaps, and download report PDF under **Reports**.
        """)

# ---------------------------------------------------------
# TAB 2: UPLOAD CV
# ---------------------------------------------------------
with tabs[1]:
    st.header("📄 Upload & Inspect Resume (CV)")
    
    uploaded_file = st.file_uploader("Upload candidate CV in PDF format", type=["pdf"])
    
    if uploaded_file is not None:
        extracted_text = CVParser.extract_text_from_pdf(uploaded_file)
        st.session_state.raw_cv_text = extracted_text
        st.success(f"CV successfully parsed ({len(extracted_text)} characters extracted).")

    raw_input_area = st.text_area(
        "Extracted CV Text (Editable)",
        value=st.session_state.raw_cv_text,
        height=300,
        help="Extracted raw text from uploaded PDF or manual entry."
    )
    st.session_state.raw_cv_text = raw_input_area

    if st.session_state.raw_cv_text:
        structured = CVParser.parse_structured_cv(st.session_state.raw_cv_text)
        st.subheader("Extracted Section Verification")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Contact Info", "Found" if structured["contact_info"]["email"] != "Not found" else "Missing")
        c2.metric("Skills Section", "Detected" if structured["skills"] else "Not Found")
        c3.metric("Experience Section", "Detected" if structured["experience"] else "Not Found")
        c4.metric("Education Section", "Detected" if structured["education"] else "Not Found")

# ---------------------------------------------------------
# TAB 3: CV ANALYSIS
# ---------------------------------------------------------
with tabs[2]:
    st.header("📊 In-Depth CV Analysis & ATS Scoring")
    
    if not st.session_state.raw_cv_text:
        st.warning("Please upload a CV under the 'Upload CV' tab first.")
    else:
        if st.button("🔍 Analyze CV Quality Now", type="primary"):
            with st.spinner("CV Analysis Agent executing tool calculations & deep reasoning..."):
                res = workflow.run_pipeline(
                    user_query="Analyze uploaded CV quality and ATS score",
                    raw_cv_text=st.session_state.raw_cv_text
                )
                st.session_state.pipeline_results = res
                st.success("CV Analysis Complete!")

        if st.session_state.pipeline_results:
            cv_out = st.session_state.pipeline_results.get("cv_analysis_output", {})
            
            c1, c2 = st.columns([1, 1])
            with c1:
                st.plotly_chart(create_ats_score_gauge(cv_out.get("score", 70)), use_container_width=True)
            with c2:
                if cv_out.get("ats_breakdown"):
                    st.plotly_chart(create_ats_breakdown_chart(cv_out["ats_breakdown"]), use_container_width=True)

            st.subheader("Detected Technical Skills & Action Verbs")
            s_col1, s_col2 = st.columns(2)
            with s_col1:
                st.write("**Extracted Tech Keywords:**")
                st.write(", ".join(cv_out.get("detected_skills", ["None detected"])))
            with s_col2:
                st.write("**Strong Action Verbs Found:**")
                st.write(", ".join(cv_out.get("action_verbs_found", ["None detected"])))

            st.subheader("Actionable CV Improvements")
            for imp in cv_out.get("actionable_improvements", []):
                st.info(f"💡 {imp}")

# ---------------------------------------------------------
# TAB 4: JOB MATCHING
# ---------------------------------------------------------
with tabs[3]:
    st.header("🎯 Job Description Matching & Skill Gap Analysis")
    
    target_role_input = st.text_input("Target Job Title", value=st.session_state.target_role)
    st.session_state.target_role = target_role_input
    
    jd_input = st.text_area(
        "Target Job Description",
        value=st.session_state.job_description,
        height=200,
        placeholder="Paste full job description requirements here..."
    )
    st.session_state.job_description = jd_input

    if st.button("🚀 Run Job Matching Agent", type="primary"):
        if not st.session_state.raw_cv_text or not st.session_state.job_description:
            st.error("Please provide both CV text and Job Description.")
        else:
            with st.spinner("Job Matching Agent analyzing skill gap matrix..."):
                res = workflow.run_pipeline(
                    user_query="Match CV against target job description",
                    raw_cv_text=st.session_state.raw_cv_text,
                    job_description=st.session_state.job_description,
                    target_role=st.session_state.target_role
                )
                st.session_state.pipeline_results = res
                st.success("Job Match Evaluation Complete!")

    if st.session_state.pipeline_results and st.session_state.pipeline_results.get("job_matching_output"):
        job_out = st.session_state.pipeline_results.get("job_matching_output", {})
        
        m_col1, m_col2 = st.columns([1, 1])
        with m_col1:
            st.metric("Job Match Percentage", f"{job_out.get('match_percentage', 0)}%", delta=job_out.get('role_alignment_level'))
            st.plotly_chart(create_skill_gap_chart(job_out.get("key_matched_skills", []), job_out.get("critical_missing_skills", [])), use_container_width=True)
        with m_col2:
            st.subheader("Critical Missing Target Skills")
            for skill in job_out.get("critical_missing_skills", []):
                st.error(f"❌ Missing: {skill}")

        st.subheader("Recommendations to Pass Screening")
        for rec in job_out.get("recommendations_to_pass_screening", []):
            st.success(f"✅ {rec}")

# ---------------------------------------------------------
# TAB 5: CAREER RECOMMENDATIONS
# ---------------------------------------------------------
with tabs[4]:
    st.header("🚀 Personalized Learning Roadmap & Career Plan")
    
    if st.button("🔥 Generate Strategic Career Plan"):
        with st.spinner("Career Recommendation Agent designing learning roadmap..."):
            res = workflow.run_pipeline(
                user_query="Generate personalized learning roadmap and career advice",
                raw_cv_text=st.session_state.raw_cv_text,
                job_description=st.session_state.job_description,
                target_role=st.session_state.target_role
            )
            st.session_state.pipeline_results = res

    if st.session_state.pipeline_results and st.session_state.pipeline_results.get("career_recommendations_output"):
        career_out = st.session_state.pipeline_results.get("career_recommendations_output", {})
        
        st.subheader("🎯 Top Suitable Job Roles")
        roles = career_out.get("suitable_job_roles", [])
        for r in roles:
            if isinstance(r, dict):
                st.markdown(f"- **{r.get('role')}**: {r.get('fit_reason')}")

        st.subheader("📅 8-Week Structured Learning Roadmap")
        roadmap = career_out.get("learning_roadmap", [])
        for phase in roadmap:
            with st.expander(f"📌 {phase.get('phase', 'Phase')} - {phase.get('focus', '')}", expanded=True):
                for item in phase.get("action_items", []):
                    st.write(f"• {item}")

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🛠️ Recommended Tech Stack")
            st.write(", ".join(career_out.get("recommended_tech_stack", [])))
        with c2:
            st.subheader("📜 Industry Certifications")
            st.write(", ".join(career_out.get("recommended_certifications", [])))

# ---------------------------------------------------------
# TAB 6: AI CAREER CHAT (RAG AGENT)
# ---------------------------------------------------------
with tabs[5]:
    st.header("💬 AI Career Guidance Chat (RAG Knowledge Engine)")
    st.caption("Ask questions about ATS guidelines, CV structure, IT career paths, or interview prep. Answers are grounded in the 22-document domain corpus.")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "sources" in msg and msg["sources"]:
                st.caption(f"📚 Sources: {', '.join(msg['sources'])}")

    user_chat_input = st.chat_input("Ask a career question (e.g. How do I format ATS bullet points for Python projects?)")
    
    if user_chat_input:
        st.session_state.chat_history.append({"role": "user", "content": user_chat_input})
        with st.chat_message("user"):
            st.write(user_chat_input)

        with st.chat_message("assistant"):
            with st.spinner("RAG Agent querying FAISS vector database..."):
                res = workflow.run_pipeline(
                    user_query=user_chat_input,
                    raw_cv_text=st.session_state.raw_cv_text,
                    job_description=st.session_state.job_description
                )
                rag_out = res.get("rag_knowledge_output", {})
                answer = rag_out.get("answer", "I couldn't locate specific information for that query.")
                sources = rag_out.get("sources", [])

                st.write(answer)
                if sources:
                    st.caption(f"📚 Sources: {', '.join(sources)}")

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })

# ---------------------------------------------------------
# TAB 7: REPORTS & INTER-AGENT LOGS
# ---------------------------------------------------------
with tabs[6]:
    st.header("📥 Full Evaluation Summary, Logs & Export")
    
    if st.session_state.pipeline_results:
        state_data = st.session_state.pipeline_results
        
        st.subheader("Inter-Agent Communication Log (JSON Messages)")
        logs = state_data.get("execution_logs", [])
        st.markdown('<div class="agent-log-box">', unsafe_allow_html=True)
        st.json(logs)
        st.markdown('</div>', unsafe_allow_html=True)

        st.divider()

        st.subheader("Quality Audit Verdict (Reflection Agent)")
        ref_out = state_data.get("reflection_output", {})
        c1, c2 = st.columns(2)
        c1.metric("Audit Score", f"{ref_out.get('quality_score', 90)}/100")
        c2.metric("Quality Gate Passed", "YES ✅" if ref_out.get("passed_quality_gate") else "NO ❌")
        
        for note in ref_out.get("critique_notes", []):
            st.caption(f"✔️ {note}")

        st.divider()

        st.subheader("Download Generated Career Report")
        pdf_bytes = generate_pdf_report(state_data)
        st.download_button(
            label="📥 Download Full PDF Report",
            data=pdf_bytes,
            file_name="AI_Career_Analysis_Report.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Run an analysis in CV Analysis or Job Matching to populate full reports & logs.")
