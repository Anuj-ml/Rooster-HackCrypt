from typing import List
import json
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser

class DocumentProcessor:
    def __init__(self, llm_model):
        self.llm = llm_model
        # Larger chunks = fewer API calls (reduces from 145 to ~50 chunks)
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
        self._init_chain()

    def _init_chain(self):
        """Initializes the proposition extraction chain with JSON output."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a text decomposition expert. Your task is to break down text into atomic facts.

Instructions:
1. Read the text carefully
2. Extract distinct, standalone facts
3. Each fact should be self-contained and understandable without context
4. Resolve all pronouns (replace "it", "he", "she" with actual nouns)
5. Split compound sentences into separate facts
6. Maintain factual accuracy - do not add information

Output format - Return ONLY valid JSON:
{{"facts": ["fact 1", "fact 2", "fact 3"]}}

Example:
Input: "Einstein developed relativity. It changed physics."
Output: {{"facts": ["Einstein developed the theory of relativity.", "The theory of relativity changed physics."]}}

Return ONLY the JSON, no other text."""),
            ("user", "{input_text}")
        ])
        self.chain = prompt | self.llm | StrOutputParser()
    
    def _parse_propositions(self, llm_output: str) -> List[str]:
        """Parse propositions from LLM output, handling various formats."""
        try:
            # Try to find JSON in the output
            json_match = re.search(r'\{[^}]*"(facts|propositions)"[^}]*\}', llm_output, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                return data.get("facts", data.get("propositions", []))
            
            # If no JSON found, try direct JSON parse
            data = json.loads(llm_output.strip())
            return data.get("facts", data.get("propositions", []))
            
        except json.JSONDecodeError:
            # Fallback: split by newlines and clean
            lines = [line.strip() for line in llm_output.split('\n') if line.strip()]
            # Filter out non-content lines
            propositions = [
                line for line in lines 
                if line and not line.startswith('{') and not line.startswith('}')
                and len(line) > 10  # Ignore very short lines
            ]
            return propositions if propositions else [llm_output]

    def load_and_split(self, file_path: str) -> List[Document]:
        """Loads PDF and creates Parent Documents."""
        loader = PyPDFLoader(file_path)
        return loader.load_and_split(self.splitter)

    def generate_propositions(self, docs: List[Document]) -> List[List[str]]:
        """
        Batch processes docs to generate propositions with rate limiting.
        Falls back to conventional RAG (raw chunks) immediately on API limit errors.
        Returns a list of proposition lists (one list per parent doc).
        """
        import time
        from groq import RateLimitError
        
        print(f"--- Decomposing {len(docs)} Parent Documents ---")
        
        # Process in smaller batches to avoid rate limits
        results = []
        batch_size = 3  # Process 3 docs at a time
        rate_limit_hit = False  # Track if we've hit rate limits
        
        for i in range(0, len(docs), batch_size):
            batch = docs[i:i+batch_size]
            batch_input = [{"input_text": d.page_content} for d in batch]
            batch_num = i // batch_size + 1
            total_batches = (len(docs) - 1) // batch_size + 1
            
            print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} documents)...")
            
            # If we've already hit rate limits, skip decomposition for all remaining batches
            if rate_limit_hit:
                print(f"⚠ Using conventional RAG (raw chunks) - API limit reached")
                results.extend([[doc.page_content] for doc in batch])
                continue
            
            # Try LLM decomposition with limited retries
            max_retries = 3
            batch_success = False
            
            for attempt in range(max_retries):
                try:
                    # Get raw string outputs from LLM
                    raw_outputs = self.chain.batch(batch_input)
                    
                    # Parse each output to extract propositions
                    batch_propositions = []
                    for raw_output in raw_outputs:
                        props = self._parse_propositions(raw_output)
                        batch_propositions.append(props)
                    
                    results.extend(batch_propositions)
                    print(f"✓ Batch {batch_num} completed successfully")
                    batch_success = True
                    break
                    
                except RateLimitError as e:
                    print(f"⚠ API rate limit exceeded!")
                    print(f"⚠ Switching to conventional RAG mode (no LLM decomposition)")
                    print(f"   All remaining batches will use raw document chunks")
                    
                    # Fall back to raw chunks for current batch
                    results.extend([[doc.page_content] for doc in batch])
                    
                    # Mark that we've hit rate limits - all future batches use raw chunks
                    rate_limit_hit = True
                    batch_success = True
                    break
                        
                except Exception as e:
                    error_msg = str(e)[:100]  # Truncate long error messages
                    print(f"✗ Error on attempt {attempt + 1}/{max_retries}: {error_msg}")
                    
                    # After 3 attempts, fall back to raw chunks
                    if attempt >= max_retries - 1:
                        print(f"⚠ Falling back to conventional RAG for batch {batch_num}")
                        results.extend([[doc.page_content] for doc in batch])
                        batch_success = True
                        break
                    
                    if attempt < max_retries - 1:
                        wait_time = 3
                        print(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
            
            # If all retries failed and fallback wasn't triggered, raise error
            if not batch_success:
                print(f"⚠ Failed to process batch {batch_num}, using raw chunks")
                results.extend([[doc.page_content] for doc in batch])
            
            # Add delay between batches (only if not in fallback mode)
            if not rate_limit_hit and i + batch_size < len(docs):
                delay = 5
                print(f"Waiting {delay} seconds before next batch...")
                time.sleep(delay)
        
        print(f"✓ Successfully processed all {len(docs)} documents!")
        return results