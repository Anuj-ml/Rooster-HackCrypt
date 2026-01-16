from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from schemas import PropositionList

class DocumentProcessor:
    def __init__(self, llm_model):
        self.llm = llm_model
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        self._init_chain()

    def _init_chain(self):
        """Initializes the proposition extraction chain."""
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

    def load_and_split(self, file_path: str) -> List[Document]:
        """Loads PDF and creates Parent Documents."""
        loader = PyPDFLoader(file_path)
        return loader.load_and_split(self.splitter)

    def generate_propositions(self, docs: List[Document]) -> List[List[str]]:
        """
        Batch processes docs to generate propositions.
        Returns a list of proposition lists (one list per parent doc).
        """
        print(f"--- Decomposing {len(docs)} Parent Documents ---")
        # In production, use .batch() with concurrency limits
        batch_input = [{"input_text": d.page_content} for d in docs]
        results = self.chain.batch(batch_input)
        return [r.propositions for r in results]