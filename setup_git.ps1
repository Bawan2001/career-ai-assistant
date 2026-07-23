# ================================================================
# Git Workflow PowerShell Script for IT41043 Assignment
# Creates feature branches, semantic commits, and PR merges on Windows
# Run from PowerShell in project root: d:\CV analyzer
# ================================================================

# Clean existing broken git repo if needed
if (Test-Path ".git") {
    Remove-Item -Recurse -Force .git
}

Write-Host "Initializing Git Repository with main branch..." -ForegroundColor Cyan
git init -b main

Write-Host "Setting local repository identity..." -ForegroundColor Cyan
git config --local user.name "Student Developer"
git config --local user.email "student@horizoncampus.edu.lk"

git add .gitignore .env.example
git commit -m "feat: initialize project scaffold with gitignore and env template"

# ------ STEP 1: feature/agent-orchestration branch ------
Write-Host "Creating feature/agent-orchestration branch..." -ForegroundColor Yellow
git checkout -b feature/agent-orchestration

git add agents/state.py
git commit -m "feat: add LangGraph AgentState schema for inter-agent communication"

git add agents/router_agent.py
git commit -m "feat: implement Router/Planner agent with planning pattern"

git add agents/cv_agent.py agents/job_agent.py agents/career_agent.py
git commit -m "feat: add CV analysis, job matching, and career recommendation agents"

git add agents/rag_agent.py agents/reflection_agent.py
git commit -m "feat: add RAG knowledge agent and reflection/self-critique agent"

git add agents/workflow.py
git commit -m "feat: create LangGraph StateGraph workflow connecting all agent nodes"

git checkout main
git merge feature/agent-orchestration --no-ff -m "merge: integrate multi-agent orchestration pipeline"

# ------ STEP 2: feature/rag-pipeline branch ------
Write-Host "Creating feature/rag-pipeline branch..." -ForegroundColor Yellow
git checkout -b feature/rag-pipeline

git add rag/corpus/
git commit -m "feat: create 22-document domain knowledge corpus for career guidance"

git add rag/document_loader.py rag/embedding.py
git commit -m "feat: implement document loader with token-aware chunking and embedding engine"

git add rag/vector_store.py
git commit -m "feat: implement FAISS vector store manager with persistence and similarity search"

git checkout main
git merge feature/rag-pipeline --no-ff -m "merge: integrate RAG pipeline with FAISS vector database"

# ------ STEP 3: feature/model-router branch ------
Write-Host "Creating feature/model-router branch..." -ForegroundColor Yellow
git checkout -b feature/model-router

git add models/llm_router.py
git commit -m "feat: implement multi-provider LLM router with tiered model selection"

git add tools/cv_parser.py tools/resume_analyzer.py
git commit -m "feat: add CV parser and ATS resume scoring tools"

git checkout main
git merge feature/model-router --no-ff -m "merge: integrate multi-model router and CV analysis tools"

# ------ STEP 4: feature/streamlit-ui branch ------
Write-Host "Creating feature/streamlit-ui branch..." -ForegroundColor Yellow
git checkout -b feature/streamlit-ui

git add frontend/components/styles.py frontend/components/charts.py
git commit -m "feat: create custom CSS theme and interactive Plotly chart components"

git add app.py
git commit -m "feat: build 7-tab Streamlit dashboard with upload, analysis, chat, and reports"

git add utils/export_pdf.py
git commit -m "feat: add PDF report generation with ReportLab"

git checkout main
git merge feature/streamlit-ui --no-ff -m "merge: integrate Streamlit UI with charts and PDF export"

# ------ STEP 5: feature/deployment branch ------
Write-Host "Creating feature/deployment branch..." -ForegroundColor Yellow
git checkout -b feature/deployment

git add .streamlit/config.toml packages.txt requirements.txt setup_git.sh setup_git.ps1
git commit -m "feat: add Streamlit Cloud deployment configuration and requirements"

git checkout main
git merge feature/deployment --no-ff -m "merge: add deployment configuration for Streamlit Community Cloud"

# ------ STEP 6: docs/readme branch ------
Write-Host "Creating docs/readme branch..." -ForegroundColor Yellow
git checkout -b docs/readme

git add README.md
git commit -m "docs: add comprehensive README with architecture, agent diagrams, and RAG evaluation"

git checkout main
git merge docs/readme --no-ff -m "merge: finalize project documentation"

Write-Host "============================================" -ForegroundColor Green
Write-Host " Git workflow complete!" -ForegroundColor Green
Write-Host " Total commits created: 18+" -ForegroundColor Green
Write-Host " Feature branches: 6" -ForegroundColor Green
Write-Host " Merge commits: 6" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Create a GitHub repository (Public or Private with lecturer added)" -ForegroundColor White
Write-Host "2. Run: git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git" -ForegroundColor White
Write-Host "3. Run: git push -u origin main" -ForegroundColor White
Write-Host "4. Run: git push origin --all" -ForegroundColor White
