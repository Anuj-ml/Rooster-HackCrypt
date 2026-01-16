"""
Doubt Solver Feature using LangGraph

Provides ELI5 (Explain Like I'm 5) explanations for student questions based on uploaded material.
Uses RAG to retrieve relevant context and LLM to generate simplified, conversational answers.
"""

from langgraph.graph import StateGraph, END
from src.models.schemas import DoubtState, DoubtInput
from langchain_core.prompts import ChatPromptTemplate


class DoubtSolverAgent:
    """
    Doubt Solver Agent using LangGraph workflow.
    
    Workflow:
    1. Retrieve relevant documents from knowledge base (filtered by pdf_source_id)
    2. Generate simplified explanation using LLM
    
    Features:
    - ELI5 (Explain Like I'm 5) explanations
    - Strictly grounded in provided material
    - Conversational and friendly tone
    - Uses analogies when helpful
    """
    
    def __init__(self, llm, knowledge_base):
        """
        Initialize the DoubtSolverAgent.
        
        Args:
            llm: Language model for generating explanations
            knowledge_base: KnowledgeBase instance for document retrieval
        """
        self.llm = llm
        self.kb = knowledge_base
        self.graph = self._build_graph()
    
    def _retrieve_node(self, state: DoubtState):
        """
        Retrieve Node: Fetch relevant documents from Knowledge Base.
        
        Uses semantic search to find documents related to the student's question.
        Strictly filters by pdf_source_id to ensure we only use the correct material.
        """
        print(f"   🔍 Retrieving context for question: '{state.user_query[:50]}...'")
        print(f"   📂 Source ID: {state.pdf_source_id}")
        
        # Use the user's question as the retrieval query
        docs = self.kb.retrieve_context(
            query=state.user_query,
            pdf_source_id=state.pdf_source_id,
            k=5  # Get top 5 relevant documents
        )
        
        if docs:
            print(f"   ✓ Retrieved {len(docs)} relevant documents")
        else:
            print(f"   ⚠ No relevant context found in source: {state.pdf_source_id}")
        
        return {"retrieved_docs": docs}
    
    def _generate_explanation_node(self, state: DoubtState):
        """
        Generate Explanation Node: Create a simplified answer using LLM.
        
        Uses ELI5 (Explain Like I'm 5) approach with analogies and simple language.
        """
        if not state.retrieved_docs:
            print(f"   ⚠ No context available - cannot answer question")
            return {
                "answer": "I couldn't find that information in your study material. "
                         "Could you try rephrasing your question or check if the right material is uploaded?"
            }
        
        # Combine retrieved documents into context
        context_str = "\n\n".join([d.page_content for d in state.retrieved_docs if d])
        
        # ELI5 explanation prompt
        prompt = ChatPromptTemplate.from_template("""You are a friendly, patient tutor helping a student understand their study material.

CONTEXT FROM TEXTBOOK:
{context}

STUDENT'S QUESTION:
{user_query}

YOUR TASK:
1. Answer the question using ONLY the information in the provided context
2. Explain it simply, as if explaining to a 5-year-old ({simplification_level} style)
3. Use everyday analogies to make complex concepts relatable
4. Break down complicated ideas into simple steps
5. Be conversational and encouraging
6. If the answer is NOT in the context, say: "I couldn't find that in your study material."

IMPORTANT:
- Use simple words and short sentences
- Give real-world examples when possible
- Make it easy to understand
- Stay positive and encouraging
- Never make up information not in the context

Provide your explanation:""")
        
        print(f"   🧠 Generating {state.simplification_level} explanation...")
        
        try:
            response = self.llm.invoke(
                prompt.format(
                    context=context_str,
                    user_query=state.user_query,
                    simplification_level=state.simplification_level
                )
            )
            
            answer = response.content.strip()
            
            if answer:
                print(f"   ✓ Generated explanation ({len(answer)} characters)")
            else:
                print(f"   ⚠ Generated empty response")
                answer = "I had trouble generating an explanation. Please try asking your question differently."
            
            return {"answer": answer}
            
        except Exception as e:
            print(f"   ✗ Explanation generation failed: {str(e)[:200]}")
            return {
                "answer": f"Sorry, I encountered an error while trying to answer your question: {str(e)[:100]}"
            }
    
    def _build_graph(self):
        """Build the LangGraph workflow: retrieve → generate → END."""
        workflow = StateGraph(DoubtState)
        
        # Add Nodes
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("generate_explanation", self._generate_explanation_node)
        
        # Define Edges: retrieve → generate_explanation → END
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate_explanation")
        workflow.add_edge("generate_explanation", END)
        
        return workflow.compile()
    
    def solve_doubt(self, input_data: DoubtInput) -> dict:
        """
        Public API to solve a student's doubt.
        
        Args:
            input_data: DoubtInput with question, pdf_source_id, and session_id
            
        Returns:
            Dictionary with session_id, question, answer, and source_id
        """
        print(f"\n{'='*60}")
        print(f"💡 DOUBT SOLVER")
        print(f"{'='*60}")
        
        # Create state from input
        state = DoubtState(
            session_id=input_data.session_id,
            pdf_source_id=input_data.pdf_source_id,
            user_query=input_data.question,
            simplification_level="ELI5"
        )
        
        # Run the graph
        result = self.graph.invoke(state)
        
        print(f"{'='*60}\n")
        
        # Return formatted response
        return {
            "session_id": result.get("session_id"),
            "question": result.get("user_query"),
            "answer": result.get("answer", "No answer generated."),
            "source_id": result.get("pdf_source_id"),
            "context_found": len(result.get("retrieved_docs", [])) > 0
        }
