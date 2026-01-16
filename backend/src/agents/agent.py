from langgraph.graph import StateGraph, END
from src.models.schemas import AgentState, QuizOutput
from langchain_core.prompts import ChatPromptTemplate


class QuizAgent:
    """
    Quiz Generation Agent using LangGraph workflow.
    
    Workflow:
    1. Retrieve relevant documents from knowledge base
    2. Generate quiz questions using LLM with structured output
    
    Features:
    - State machine architecture (LangGraph)
    - Difficulty-aware question generation
    - Strict formatting for clean quiz output
    """
    
    def __init__(self, llm, knowledge_base):
        """
        Initialize the QuizAgent.
        
        Args:
            llm: Language model for quiz generation
            knowledge_base: KnowledgeBase instance for document retrieval
        """
        self.llm = llm
        self.kb = knowledge_base
        self.graph = self._build_graph()

    def _retrieve_node(self, state: AgentState):
        """
        Retrieve Node: Fetch relevant documents from Knowledge Base.
        
        Uses semantic search to find documents related to the topic.
        Special case: If topic is "default", retrieves from entire document.
        """
        if state.topic.lower() == "default":
            print(f"   🔍 Retrieving context from: ENTIRE DOCUMENT (default mode)")
        else:
            print(f"   🔍 Retrieving context for: {state.topic}")
        
        print(f"   📂 Source ID: {state.pdf_source_id}")
        
        docs = self.kb.retrieve_context(
            query=state.topic,
            pdf_source_id=state.pdf_source_id
        )
        
        if docs:
            print(f"   ✓ Retrieved {len(docs)} relevant documents")
        else:
            if state.topic.lower() == "default":
                print(f"   ⚠ No documents found in source: {state.pdf_source_id}")
            else:
                print(f"   ⚠ No documents found for topic: {state.topic}")
        
        return {"retrieved_docs": docs}

    def _generate_node(self, state: AgentState):
        """
        Generate Node: Create quiz questions using LLM.
        
        Uses strict formatting prompt to ensure clean output.
        """
        if not state.retrieved_docs:
            print(f"   ✗ No context available for quiz generation")
            return {"generated_quiz": None}

        context_str = "\n\n".join([d.page_content for d in state.retrieved_docs if d])
        
        # Strict formatting prompt for clean quiz output
        prompt = ChatPromptTemplate.from_template("""You are a strict quiz generator. Create EXACTLY 5 multiple choice questions.

CRITICAL FORMATTING RULES (MUST FOLLOW):
1. Each question must have EXACTLY 4 options
2. Options must be PLAIN TEXT only - absolutely NO prefixes like "A)", "1.", "(a)", "Option 1:", etc.
3. Each option should be a complete, standalone answer text
4. The correct_answer field must EXACTLY match one of the 4 options word-for-word
5. Questions should be self-contained - never reference "the passage" or "according to the text"
6. Explanations should be concise but informative (1-2 sentences)

DIFFICULTY GUIDELINES:
- EASY: Basic recall questions, straightforward facts from the context
- MEDIUM: Understanding and application, some analysis required
- HARD: Complex analysis, synthesis of multiple concepts, deeper reasoning

CONTEXT:
{context}

TASK:
Generate 5 {difficulty} difficulty questions about "{topic}" based on the context above.

Remember:
- Options should be plain text without any numbering or lettering
- The correct_answer must exactly match one option
- Questions should test understanding, not just memorization

Return ONLY valid JSON in this exact format:
{{
  "questions": [
    {{
      "question": "question text",
      "options": ["option1", "option2", "option3", "option4"],
      "correct_answer": "option1",
      "explanation": "explanation text"
    }}
  ]
}}""")
        
        print(f"   🧠 Generating {state.current_difficulty} questions...")
        
        try:
            # Use JSON mode instead of structured output for better Groq compatibility
            response = self.llm.invoke(
                prompt.format(
                    context=context_str,
                    difficulty=state.current_difficulty,
                    topic=state.topic
                ),
                response_format={"type": "json_object"}
            )
            
            # Parse JSON response
            import json
            result_dict = json.loads(response.content)
            
            # Convert to QuizOutput
            from src.models.schemas import QuizQuestion
            questions = [
                QuizQuestion(**q) for q in result_dict.get("questions", [])
            ]
            
            quiz_output = QuizOutput(questions=questions)
            
            if quiz_output and quiz_output.questions:
                print(f"   ✓ Generated {len(quiz_output.questions)} questions")
            
            return {"generated_quiz": quiz_output}
            
        except Exception as e:
            print(f"   ✗ Quiz generation failed: {str(e)[:200]}")
            return {"generated_quiz": None}

    def _build_graph(self):
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add Nodes
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("generate", self._generate_node)
        
        # Define Edges: retrieve → generate → END
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        
        return workflow.compile()

    def run_session(self, session_input: dict):
        """Public API to run the agent."""
        # Convert dict input to Pydantic State
        state = AgentState(**session_input)
        return self.graph.invoke(state)