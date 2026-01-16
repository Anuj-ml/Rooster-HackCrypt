from langgraph.graph import StateGraph, END
from schemas import AgentState, QuizOutput
from langchain_core.prompts import ChatPromptTemplate

class QuizAgent:
    def __init__(self, llm, knowledge_base):
        self.llm = llm
        self.kb = knowledge_base
        self.graph = self._build_graph()

    def _retrieve_node(self, state: AgentState):
        """Node: Fetch data from Knowledge Base."""
        docs = self.kb.retrieve_context(
            query=state.topic,
            pdf_source_id=state.pdf_source_id
        )
        # Update state (Pydantic model requires strict type, so we return dict to update)
        return {"retrieved_docs": docs}

    def _generate_node(self, state: AgentState):
        """Node: Generate Quiz JSON."""
        if not state.retrieved_docs:
            return {"generated_quiz": None} # Or handle error

        context_str = "\n\n".join([d.page_content for d in state.retrieved_docs if d])
        
        prompt = ChatPromptTemplate.from_template("""
        You are a strict quiz generator.
        Context: {context}
        
        Task: Create 5 {difficulty} multiple choice questions about "{topic}".
        Ensure questions require reasoning based on the context.
        """)
        
        chain = prompt | self.llm.with_structured_output(QuizOutput)
        
        response = chain.invoke({
            "context": context_str,
            "difficulty": state.current_difficulty,
            "topic": state.topic
        })
        
        return {"generated_quiz": response}

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        # Add Nodes
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("generate", self._generate_node)
        
        # Define Edges
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        
        return workflow.compile()

    def run_session(self, session_input: dict):
        """Public API to run the agent."""
        # Convert dict input to Pydantic State
        state = AgentState(**session_input)
        return self.graph.invoke(state)