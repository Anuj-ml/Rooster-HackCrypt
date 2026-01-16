# 🔍 ROOSTER-HACKCRYPT PROJECT - COMPLETE DETAILED ANALYSIS

**Analysis Date**: January 16, 2026  
**Repository**: Anuj-ml/Rooster-HackCrypt  
**Branch**: main

---

## **📋 PROJECT OVERVIEW**

This is a **HackCrypt hackathon project** called **Rooster**, which appears to be an **AI-Powered Adaptive Quiz Generation System** designed for educational purposes. The system uses **Retrieval-Augmented Generation (RAG)** with **Google's Gemini AI models** to create personalized quizzes from PDF educational materials.

---

## **🏗️ PROJECT ARCHITECTURE**

The project follows a **modular backend architecture** with a clean separation of concerns:

1. **Data Ingestion & Processing Layer** ([pre_processor.py](backend/pre_processor.py))
2. **Storage & Retrieval Layer** ([storage.py](backend/storage.py))
3. **Schema Definitions** ([schemas.py](backend/schemas.py))
4. **Agent Logic Layer** ([agent.py](backend/agent.py))
5. **Main Orchestration** ([ingestion_main.py](backend/ingestion_main.py))

---

## **📁 DETAILED FILE-BY-FILE BREAKDOWN**

### **1. [requirements.txt](backend/requirements.txt) - Dependencies**

**Purpose**: Defines all Python package dependencies needed for the project.

**Key Dependencies Analysis**:

- **LangChain Ecosystem** (`langchain>=0.1.0`, `langgraph>=0.0.40`):
  - **LangChain**: Framework for building LLM-powered applications
  - **LangGraph**: State machine library for building multi-step AI agents with graph-based workflows
  
- **Vector Database** (`chromadb>=0.4.24`):
  - ChromaDB is an open-source embedding database for vector similarity search
  - Used to store and retrieve document embeddings efficiently
  
- **LLM Providers**:
  - `langchain-google-genai`: Integration with Google's Gemini models
  - `langchain-community`: Community-contributed LangChain integrations
  
- **Embeddings** (`sentence-transformers`):
  - Free, local embedding models (though the code actually uses Google's embedding API)
  - Converts text into numerical vectors for semantic search
  
- **PDF Processing**:
  - `unstructured[pdf]`: Advanced PDF parsing with structure detection
  - `pypdf`: Pure Python PDF reader
  - `pytesseract`: OCR (Optical Character Recognition) for scanned PDFs
  - `pdf2image`: Converts PDF pages to images for OCR
  - `pillow`: Image processing library
  
- **Utilities**:
  - `python-dotenv`: Loads environment variables from `.env` file

---

### **2. [schemas.py](backend/schemas.py) - Data Models**

**Purpose**: Defines all data structures using Pydantic models for type safety and validation.

**Detailed Schema Breakdown**:

#### **A. `PropositionList`**
```python
class PropositionList(BaseModel):
    propositions: List[str]
```
- **Purpose**: Output schema for the document decomposition step
- **What it holds**: A list of "atomic facts" extracted from text chunks
- **Why it exists**: The LLM needs a structured format to output decomposed facts
- **Example output**: 
  ```python
  PropositionList(propositions=[
      "Newton's Third Law states that for every action, there is an equal and opposite reaction.",
      "This law applies to all forces in the universe.",
      "The law explains rocket propulsion."
  ])
  ```

#### **B. `QuizQuestion` & `QuizOutput`**
```python
class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str

class QuizOutput(BaseModel):
    questions: List[QuizQuestion]
```
- **Purpose**: Structures the quiz generation output
- **What it holds**: Complete quiz with questions, multiple choice options, answers, and explanations
- **Why it exists**: Forces the LLM to generate properly formatted quizzes
- **Example**:
  ```python
  QuizOutput(questions=[
      QuizQuestion(
          question="What does Newton's Third Law state?",
          options=["Action-Reaction", "Inertia", "F=ma", "Gravity"],
          correct_answer="Action-Reaction",
          explanation="Newton's Third Law specifically deals with action-reaction pairs."
      )
  ])
  ```

#### **C. `AgentState`**
```python
class AgentState(BaseModel):
    session_id: str              # Unique identifier for student's quiz session
    pdf_source_id: str            # Which PDF to pull questions from
    current_difficulty: str       # 'EASY', 'MEDIUM', 'HARD'
    topic: str                    # What topic the student wants to be quizzed on
    retrieved_docs: List[Document] # Context fetched from knowledge base
    generated_quiz: Optional[QuizOutput]  # Final quiz result
```
- **Purpose**: Maintains state as data flows through the agent workflow
- **Why it's critical**: LangGraph uses this to pass information between graph nodes
- **Design pattern**: This is a **state machine** where each node reads and updates the state
- **The `arbitrary_types_allowed`**: Allows non-Pydantic types (like LangChain's `Document` objects) in the model

---

### **3. [storage.py](backend/storage.py) - Knowledge Base (RAG Storage)**

**Purpose**: Implements a **Multi-Vector Retrieval System** that separates storage of small, searchable propositions from large parent documents.

#### **🧠 The Multi-Vector Retrieval Strategy**

This is the **CORE INNOVATION** of the project. Here's why it matters:

**Traditional RAG Problem**:
- Store large chunks → poor retrieval precision (too much irrelevant context)
- Store small chunks → poor generation quality (not enough context)

**This Project's Solution**:
- **Store small propositions in vector DB** → Better retrieval precision
- **Store large parent documents separately** → Better context for generation
- **Link them via UUIDs** → Get best of both worlds

#### **Detailed Code Analysis**:

**A. Initialization**:
```python
def __init__(self, embedding_model):
    self.vectorstore = Chroma(
        collection_name="propositions_db",
        embedding_function=embedding_model
    )
    self.docstore = InMemoryByteStore()
    self.id_key = "doc_id"
```
- **Two separate stores**:
  - `vectorstore`: ChromaDB for semantic search of propositions
  - `docstore`: In-memory key-value store for parent documents
- **Comment notes**: Production should use RedisStore instead of InMemoryByteStore (for persistence)

**B. `index_document()` Method**:
```python
def index_document(self, parent_docs, all_propositions, pdf_source_id):
    doc_ids = [str(uuid.uuid4()) for _ in parent_docs]  # Generate unique IDs
    
    for i, (parent_doc, propositions) in enumerate(zip(parent_docs, all_propositions)):
        parent_id = doc_ids[i]
        parent_doc.metadata["pdf_source_id"] = pdf_source_id
        
        for prop in propositions:
            new_doc = Document(
                page_content=prop,
                metadata={
                    self.id_key: parent_id,
                    "pdf_source_id": pdf_source_id
                }
            )
            proposition_docs.append(new_doc)
    
    self.docstore.mset(list(zip(doc_ids, parent_docs)))
    self.vectorstore.add_documents(proposition_docs)
```

**What happens step-by-step**:
1. Generate UUID for each parent document
2. For each proposition:
   - Create a new Document with the proposition text
   - Tag it with the parent's UUID and the PDF source
3. Store parent documents in docstore (UUID → full document)
4. Store propositions in vectorstore (embedding → proposition + metadata)

**Critical metadata**: The `pdf_source_id` allows filtering by which PDF the content came from

**C. `retrieve_context()` Method**:
```python
def retrieve_context(self, query, pdf_source_id, k=5):
    # Step 1: Vector search for propositions
    results = self.vectorstore.similarity_search(
        query, 
        k=k,
        filter={"pdf_source_id": pdf_source_id}
    )
    
    # Step 2: Extract parent IDs
    parent_ids = list(set([doc.metadata[self.id_key] for doc in results]))
    
    # Step 3: Fetch full parent documents
    return self.docstore.mget(parent_ids)
```

**The retrieval flow**:
1. **Search**: Find top K propositions semantically similar to query
2. **Filter**: Only from the specified PDF source
3. **Extract**: Get unique parent document IDs from propositions
4. **Fetch**: Retrieve full parent documents from docstore
5. **Return**: Full context (not just propositions) to the LLM

---

### **4. [pre_processor.py](backend/pre_processor.py) - Document Processing**

**Purpose**: Handles PDF ingestion and proposition decomposition using LLMs.

#### **Detailed Analysis**:

**A. Initialization**:
```python
def __init__(self, llm_model):
    self.llm = llm_model
    self.splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    self._init_chain()
```
- **Text Splitter**:
  - `chunk_size=1000`: Splits documents into ~1000 character chunks
  - `chunk_overlap=100`: Overlaps chunks by 100 chars to avoid cutting mid-sentence
  - **Recursive**: Tries to split on paragraphs, then sentences, then words
  
**B. The Proposition Chain**:
```python
def _init_chain(self):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Decompose the following text into distinct, standalone "atomic facts" (propositions).
        Rules:
        1. Resolve pronouns (e.g., replace 'it' with the actual noun).
        2. Split compound sentences.
        3. Maintain strictly factual accuracy.
        """),
        ("user", "Text: {input_text}")
    ])
    self.chain = prompt | self.llm.with_structured_output(PropositionList)
```

**What's happening**:
- **Prompt Engineering**: Instructs LLM to create atomic, standalone facts
- **Key rule - "Resolve pronouns"**: 
  - Original: "Newton discovered gravity. It explains falling objects."
  - Decomposed: "Newton discovered gravity." + "Gravity explains falling objects."
- **Structured Output**: Forces LLM to return `PropositionList` Pydantic model
- **The `|` operator**: LangChain's pipe operator chains prompt → LLM

**C. `load_and_split()` Method**:
```python
def load_and_split(self, file_path):
    loader = PyPDFLoader(file_path)
    return loader.load_and_split(self.splitter)
```
- Loads PDF and immediately splits into parent chunks
- Returns list of LangChain `Document` objects

**D. `generate_propositions()` Method**:
```python
def generate_propositions(self, docs):
    batch_input = [{"input_text": d.page_content} for d in docs]
    results = self.chain.batch(batch_input)
    return [r.propositions for r in results]
```
- **Batch processing**: Sends all chunks to LLM in one call for efficiency
- Returns nested list: `[[props_for_chunk_1], [props_for_chunk_2], ...]`
- **Note**: Comment mentions production should use concurrency limits to avoid rate limiting

---

### **5. [agent.py](backend/agent.py) - Quiz Generation Agent**

**Purpose**: Implements a LangGraph-based agent that retrieves context and generates quizzes.

#### **🤖 Understanding the Agent Architecture**:

This uses **LangGraph**, which models AI workflows as **directed graphs** where:
- **Nodes** = Functions that do work
- **Edges** = Control flow between nodes
- **State** = Data passed between nodes

#### **Detailed Code Breakdown**:

**A. `_retrieve_node()`**:
```python
def _retrieve_node(self, state: AgentState):
    docs = self.kb.retrieve_context(
        query=state.topic,
        pdf_source_id=state.pdf_source_id
    )
    return {"retrieved_docs": docs}
```
- **Input**: Current `AgentState` (contains topic, pdf_id)
- **Action**: Calls knowledge base to get relevant documents
- **Output**: Dictionary that updates state with retrieved docs
- **Why dict?**: LangGraph merges return dict into state

**B. `_generate_node()`**:
```python
def _generate_node(self, state: AgentState):
    if not state.retrieved_docs:
        return {"generated_quiz": None}
    
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
```

**Step-by-step**:
1. **Guard clause**: Return None if no context found
2. **Context assembly**: Join all retrieved documents with double newlines
3. **Dynamic prompt**: Injects context, difficulty, and topic
4. **Structured generation**: Forces LLM to output `QuizOutput` format
5. **State update**: Returns quiz in dict to update state

**C. `_build_graph()`**:
```python
def _build_graph(self):
    workflow = StateGraph(AgentState)
    
    workflow.add_node("retrieve", self._retrieve_node)
    workflow.add_node("generate", self._generate_node)
    
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    
    return workflow.compile()
```

**The workflow graph**:
```
START → retrieve → generate → END
```

**Why use a graph?**:
- **Extensibility**: Easy to add nodes like "difficulty_adjustment", "feedback_processing"
- **Modularity**: Each node is testable independently
- **Visualization**: LangGraph can visualize this workflow
- **State management**: Handles state passing automatically

**D. `run_session()`**:
```python
def run_session(self, session_input: dict):
    state = AgentState(**session_input)
    return self.graph.invoke(state)
```
- Public API to run the agent
- Converts dict input to Pydantic model
- Invokes the compiled graph

---

### **6. [ingestion_main.py](backend/ingestion_main.py) - Main Orchestration**

**Purpose**: **Entry point** that wires everything together and provides high-level APIs.

#### **Detailed Analysis**:

**A. Configuration Section**:
```python
LLM_MODEL = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    convert_system_message_to_human=True
)

EMBEDDING_MODEL = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004"
)
```

**Model Choices Explained**:
- **Gemini 1.5 Flash**: 
  - Google's fast, cost-effective model
  - Perfect for high-volume tasks (processing many PDFs)
  - Good reasoning for quiz generation
  - `temperature=0`: Deterministic output (no creativity)
  - `convert_system_message_to_human`: Compatibility flag for older LangChain

- **text-embedding-004**:
  - Google's latest embedding model (as of project creation)
  - Generates 768-dimensional vectors
  - Optimized for semantic search

**B. Dependency Injection**:
```python
processor = DocumentProcessor(llm_model=LLM_MODEL)
kb = KnowledgeBase(embedding_model=EMBEDDING_MODEL)
agent = QuizAgent(llm=LLM_MODEL, knowledge_base=kb)
```
- **Design pattern**: Constructor injection for testability
- All components share the same LLM and KB instances

**C. `upload_new_material()` Function**:
```python
def upload_new_material(pdf_path: str, source_id: str):
    parent_docs = processor.load_and_split(pdf_path)
    propositions = processor.generate_propositions(parent_docs)
    kb.index_document(parent_docs, propositions, source_id)
```

**The Teacher Workflow**:
1. **Input**: PDF file path + unique source ID
2. **Load**: Read PDF and split into chunks
3. **Decompose**: Use Gemini to extract atomic facts
4. **Index**: Store in knowledge base for retrieval

**Use case**: Teacher uploads "Chapter 4: Newton's Laws" with ID `"phy_004"`

**D. `student_request_quiz()` Function**:
```python
def student_request_quiz(session_id: str, pdf_id: str, topic: str):
    input_data = {
        "session_id": session_id,
        "pdf_source_id": pdf_id,
        "current_difficulty": "HARD",
        "topic": topic
    }
    
    result = agent.run_session(input_data)
    final_quiz = result['generated_quiz']
    return final_quiz
```

**The Student Workflow**:
1. **Input**: Session ID, PDF ID, topic
2. **Prepare state**: Create initial agent state
3. **Run agent**: Execute retrieve → generate workflow
4. **Extract quiz**: Get generated quiz from final state
5. **Return**: Quiz ready for student

**Note in code**: "In a real app, fetch this from your 'AdaptiveSessions' DB" 
- This suggests planned database integration for tracking student progress

---

## **🔄 COMPLETE SYSTEM FLOW**

### **Phase 1: Material Upload (Teacher Side)**
```
Teacher uploads PDF
       ↓
PDF → PyPDFLoader → Split into chunks (parent docs)
       ↓
Chunks → Gemini Flash → Atomic propositions (decomposed facts)
       ↓
Link: Each proposition → parent document UUID
       ↓
Store: Propositions → ChromaDB (vector search)
       Parent docs → InMemoryStore (key-value)
```

### **Phase 2: Quiz Generation (Student Side)**
```
Student requests quiz on "Newton's Laws" from "phy_004"
       ↓
Agent State: {topic, pdf_id, difficulty}
       ↓
RETRIEVE NODE:
  Query: "Newton's Laws" + filter: pdf_id="phy_004"
       ↓
  ChromaDB → Find similar propositions → Extract parent IDs
       ↓
  DocStore → Fetch full parent documents
       ↓
GENERATE NODE:
  Context + Topic + Difficulty → Gemini Flash
       ↓
  Gemini outputs structured QuizOutput (5 questions)
       ↓
Return quiz to student
```

---

## **🎯 DESIGN PATTERNS & BEST PRACTICES IDENTIFIED**

1. **Separation of Concerns**: Each module has a single responsibility
2. **Dependency Injection**: All dependencies passed via constructors
3. **Type Safety**: Pydantic models enforce data contracts
4. **Structured Output**: LLMs forced to output validated JSON
5. **Multi-Vector Retrieval**: Advanced RAG strategy
6. **State Machine Pattern**: LangGraph for workflow orchestration
7. **Batch Processing**: Efficient LLM calls via `.batch()`
8. **Metadata Filtering**: Critical for multi-tenant systems

---

## **⚠️ CURRENT ISSUES & BUGS**

### **1. ❌ CRITICAL BUG - Import Error**
- **Location**: [ingestion_main.py](backend/ingestion_main.py) Line 6
- **Issue**: `from processor import DocumentProcessor`
- **Problem**: File is named `pre_processor.py`, not `processor.py`
- **Fix needed**: Change import to `from pre_processor import DocumentProcessor`

### **2. 📝 Empty .env File**
- **Location**: [.env](backend/.env)
- **Issue**: File exists but is empty
- **Missing**: `GOOGLE_API_KEY` for Gemini access
- **Impact**: Code will crash when trying to use Gemini

### **3. ⚠️ In-Memory Storage**
- **Issue**: Using `InMemoryByteStore` means data lost on restart
- **Production needs**: Persistent storage (Redis/PostgreSQL)

### **4. ⚠️ No Error Handling**
- No try-except blocks for API failures
- No handling for rate limits
- No validation of PDF file existence

### **5. ⚠️ Hardcoded Difficulty**
- **Location**: [ingestion_main.py](backend/ingestion_main.py) Line 74
- **Issue**: `"current_difficulty": "HARD"` is hardcoded
- **Comment indicates**: Should come from database

---

## **🚀 MISSING COMPONENTS (For Full Application)**

1. **Frontend**: Empty folder - needs React/Vue UI
2. **Database**: No persistent storage for:
   - User sessions
   - Student progress tracking
   - Quiz history
   - Difficulty adaptation logic
3. **API Layer**: No FastAPI/Flask REST endpoints
4. **Authentication**: No user management system
5. **Adaptive Logic**: Difficulty adjustment based on performance not implemented
6. **Analytics**: No tracking of student performance metrics

---

## **💡 INTENDED FEATURES (Based on Code Comments)**

1. **Adaptive Learning**: System should adjust difficulty based on student performance
2. **Multi-Tenant**: Multiple PDFs indexed separately (via `pdf_source_id`)
3. **Session Management**: Track student quiz sessions over time
4. **Personalization**: Topic-based quiz generation
5. **Production Scaling**: Comments mention Redis, concurrency limits

---

## **🎓 EDUCATIONAL VALUE OF THIS ARCHITECTURE**

This project demonstrates understanding of:
- **Modern RAG**: Beyond simple chunk-and-retrieve
- **LLM Orchestration**: Using LangGraph for complex workflows
- **Prompt Engineering**: Structured outputs, decomposition
- **Vector Databases**: Semantic search and filtering
- **State Management**: Pydantic models for type safety
- **Production Considerations**: Comments about scaling, persistence

---

## **🛠️ TO RUN THIS PROJECT**

### **Step 1: Fix the import bug**
Change Line 6 in [ingestion_main.py](backend/ingestion_main.py):
```python
# FROM:
from processor import DocumentProcessor

# TO:
from pre_processor import DocumentProcessor
```

### **Step 2: Add to .env**
Create/update [.env](backend/.env) with:
```
GOOGLE_API_KEY=your_api_key_here
```

### **Step 3: Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

### **Step 4: Uncomment test code in main**
In [ingestion_main.py](backend/ingestion_main.py), uncomment:
```python
if __name__ == "__main__":
    # 1. Simulate Teacher Upload
    upload_new_material("path/to/your.pdf", "pdf_001")
    
    # 2. Simulate Student Quiz
    quiz = student_request_quiz("session_123", "pdf_001", "Your Topic")
```

### **Step 5: Run**
```bash
python ingestion_main.py
```

---

## **📊 PROJECT STATUS SUMMARY**

| Component | Status | Notes |
|-----------|--------|-------|
| Backend Core | ✅ 90% Complete | Needs import fix |
| RAG System | ✅ Complete | Production-ready multi-vector retrieval |
| LLM Integration | ✅ Complete | Gemini 1.5 Flash integration |
| Frontend | ❌ Not Started | Empty folder |
| Database | ❌ Not Started | In-memory only |
| API Endpoints | ❌ Not Started | No REST API |
| Authentication | ❌ Not Started | No user system |
| Adaptive Logic | ⚠️ Planned | Framework exists, logic missing |

---

## **🎯 CONCLUSION**

This is a **well-architected hackathon project** with sophisticated RAG implementation. The core AI logic is solid and production-ready with minor modifications. Key strengths include:

- ✅ Advanced multi-vector retrieval strategy
- ✅ Proper separation of concerns
- ✅ Type-safe with Pydantic models
- ✅ Efficient batch processing
- ✅ Extensible LangGraph architecture

**Next Steps for Production**:
1. Fix import bug
2. Add frontend (React/Next.js)
3. Implement REST API (FastAPI)
4. Add persistent database (PostgreSQL + Redis)
5. Implement adaptive difficulty logic
6. Add user authentication
7. Deploy to cloud (AWS/GCP/Azure)

**Estimated Development Time**: 2-3 weeks for full production deployment
