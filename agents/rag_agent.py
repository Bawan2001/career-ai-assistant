import os
from typing import Dict, Any, List
from models.llm_router import LLMRouter
from rag.vector_store import FAISSVectorStoreManager
from agents.state import AgentState

class RAGKnowledgeAgent:
    """
    AGENT 5: RAG Knowledge Agent
    Design Pattern: Knowledge Retrieval & Grounding Pattern
    
    Responsibilities:
    - Retrieve domain-specific documents from FAISS Vector Database
    - Synthesize accurate, grounded career answers
    - Include explicit document source citations
    """

    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router
        self.vector_manager = FAISSVectorStoreManager()

    def run(self, state: AgentState) -> Dict[str, Any]:
        query = state.get("user_query", "")
        if not query:
            query = "What are the best practices for writing an ATS-friendly tech CV?"

        # 1. Retrieve top matching chunks from FAISS vector DB
        docs = self.vector_manager.similarity_search(query, k=4)
        
        context_str = ""
        sources: List[str] = []
        for i, doc in enumerate(docs, 1):
            source_name = doc.metadata.get("source", f"Document {i}")
            sources.append(os.path.basename(source_name))
            context_str += f"\n--- Source: {os.path.basename(source_name)} ---\n{doc.page_content}\n"

        prompt = f"""
You are the RAG Knowledge Agent. Answer the candidate's query strictly based on the provided domain context.

User Query: "{query}"

Retrieved Knowledge Base Context:
{context_str}

Instructions:
- Provide a clear, highly structured, professional answer.
- Reference specific facts, metrics, and frameworks from the context.
- List source references used.
"""
        answer = self.llm_router.invoke_prompt(prompt, task_tier="reasoning")

        rag_output = {
            "query": query,
            "answer": answer,
            "sources": list(set(sources)),
            "retrieved_chunks_count": len(docs)
        }

        # Inter-agent status communication
        inter_agent_msg = {
            "sender": "RAG Knowledge Agent",
            "recipient": "Reflection Agent",
            "status": "complete",
            "retrieved_sources": rag_output["sources"]
        }

        logs = state.get("execution_logs", [])
        logs.append(inter_agent_msg)

        return {
            "rag_knowledge_output": rag_output,
            "execution_logs": logs
        }
