# backend/src/rag/syllabus_loader.py

"""
Syllabus Loader Module

Parses syllabus/curriculum documents and structures the content.
Supports:
- Text files (.txt)
- PDF syllabi
- Word documents (.docx)
- Structured course outlines
"""

import os
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
import re


class SyllabusLoader:
    """Load and structure syllabus content."""
    
    def __init__(self):
        """Initialize syllabus loader."""
        self.supported_formats = ['.pdf', '.txt', '.docx']
    
    def load_syllabus(self, file_path: str) -> List[Document]:
        """
        Load syllabus from file.
        
        Args:
            file_path: Path to syllabus file
            
        Returns:
            List of documents (one per section/topic)
        """
        if not os.path.exists(file_path):
            print(f"✗ File not found: {file_path}")
            return []
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext not in self.supported_formats:
            print(f"✗ Unsupported format: {ext}")
            print(f"  Supported: {', '.join(self.supported_formats)}")
            return []
        
        print(f"\n{'─'*60}")
        print(f"📚 LOADING SYLLABUS")
        print(f"{'─'*60}")
        print(f"   File: {os.path.basename(file_path)}")
        print(f"   Format: {ext}")
        
        # Load based on format
        if ext == '.pdf':
            docs = self._load_pdf(file_path)
        elif ext == '.txt':
            docs = self._load_text(file_path)
        elif ext == '.docx':
            docs = self._load_docx(file_path)
        else:
            docs = []
        
        if docs:
            print(f"   ✓ Loaded {len(docs)} sections")
        else:
            print(f"   ✗ Failed to load syllabus")
        
        print(f"{'─'*60}")
        
        return docs
    
    def _load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF syllabus."""
        try:
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            
            # Combine all pages
            full_text = "\\n\\n".join(page.page_content for page in pages)
            
            # Structure the content
            docs = self._structure_content(full_text, file_path)
            
            return docs
        except Exception as e:
            print(f"   ✗ PDF load error: {str(e)}")
            return []
    
    def _load_text(self, file_path: str) -> List[Document]:
        """Load text syllabus."""
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            pages = loader.load()
            
            if not pages:
                return []
            
            full_text = pages[0].page_content
            
            # Structure the content
            docs = self._structure_content(full_text, file_path)
            
            return docs
        except Exception as e:
            print(f"   ✗ Text load error: {str(e)}")
            return []
    
    def _load_docx(self, file_path: str) -> List[Document]:
        """Load Word document syllabus."""
        try:
            from docx import Document as DocxDocument
            
            doc = DocxDocument(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full_text = "\\n\\n".join(paragraphs)
            
            # Structure the content
            docs = self._structure_content(full_text, file_path)
            
            return docs
        except ImportError:
            print(f"   ✗ python-docx not installed. Run: pip install python-docx")
            return []
        except Exception as e:
            print(f"   ✗ DOCX load error: {str(e)}")
            return []
    
    def _structure_content(self, text: str, source: str) -> List[Document]:
        """
        Structure syllabus content into sections.
        
        Looks for:
        - Module/Unit/Week headers
        - Topic headers
        - Chapter titles
        """
        sections = []
        
        # Split by common section markers
        patterns = [
            r'(Module \\d+:.*?)(?=Module \\d+:|$)',
            r'(Unit \\d+:.*?)(?=Unit \\d+:|$)',
            r'(Week \\d+:.*?)(?=Week \\d+:|$)',
            r'(Chapter \\d+:.*?)(?=Chapter \\d+:|$)',
            r'(Topic \\d+:.*?)(?=Topic \\d+:|$)'
        ]
        
        matched = False
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            if matches and len(matches) > 1:
                for i, match in enumerate(matches, 1):
                    # Extract title from first line
                    lines = match.strip().split('\\n')
                    title = lines[0] if lines else f"Section {i}"
                    content = match.strip()
                    
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": source,
                            "section": i,
                            "title": title,
                            "type": "syllabus_section"
                        }
                    )
                    sections.append(doc)
                
                matched = True
                break
        
        # If no structured sections found, treat as one document
        if not matched:
            doc = Document(
                page_content=text.strip(),
                metadata={
                    "source": source,
                    "section": 1,
                    "title": os.path.basename(source),
                    "type": "syllabus"
                }
            )
            sections.append(doc)
        
        return sections
    
    def extract_topics(self, docs: List[Document]) -> List[str]:
        """
        Extract topic list from syllabus documents.
        
        Args:
            docs: Syllabus documents
            
        Returns:
            List of topic strings
        """
        topics = []
        
        for doc in docs:
            # Try to extract topics from bullet points or numbered lists
            text = doc.page_content
            
            # Look for lines that start with bullets, numbers, or dashes
            lines = text.split('\\n')
            for line in lines:
                line = line.strip()
                
                # Check for list markers
                if re.match(r'^[\\-\\*•]\\s+(.+)$', line):
                    topic = re.sub(r'^[\\-\\*•]\\s+', '', line).strip()
                    if len(topic) > 10 and len(topic) < 200:
                        topics.append(topic)
                elif re.match(r'^\\d+\\.\\s+(.+)$', line):
                    topic = re.sub(r'^\\d+\\.\\s+', '', line).strip()
                    if len(topic) > 10 and len(topic) < 200:
                        topics.append(topic)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_topics = []
        for topic in topics:
            if topic.lower() not in seen:
                seen.add(topic.lower())
                unique_topics.append(topic)
        
        return unique_topics


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def load_syllabus(file_path: str) -> List[Document]:
    """
    Load syllabus from file.
    
    Args:
        file_path: Path to syllabus file
        
    Returns:
        List of documents
    """
    loader = SyllabusLoader()
    return loader.load_syllabus(file_path)


def extract_topics(file_path: str) -> List[str]:
    """
    Extract topics from syllabus.
    
    Args:
        file_path: Path to syllabus file
        
    Returns:
        List of topic strings
    """
    loader = SyllabusLoader()
    docs = loader.load_syllabus(file_path)
    return loader.extract_topics(docs)


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════════════════════

def run_demo():
    """Demo syllabus loading."""
    print("\\n📚 SYLLABUS LOADER DEMO\\n")
    
    # Example: Create a sample syllabus
    sample_file = "sample_syllabus.txt"
    
    sample_content = """Course Syllabus: Introduction to Economics

Module 1: Fundamentals of Economics
- Supply and demand
- Market equilibrium
- Consumer behavior

Module 2: Macroeconomics
- GDP and economic growth
- Inflation and unemployment
- Monetary and fiscal policy

Module 3: Microeconomics
- Market structures
- Pricing strategies
- Game theory

Module 4: International Economics
- Trade and globalization
- Exchange rates
- Balance of payments
"""
    
    with open(sample_file, 'w') as f:
        f.write(sample_content)
    
    print(f"Created sample: {sample_file}\\n")
    
    # Load syllabus
    docs = load_syllabus(sample_file)
    
    print(f"\\n📊 LOADED {len(docs)} SECTIONS:\\n")
    for doc in docs:
        print(f"• {doc.metadata['title']}")
        print(f"  Length: {len(doc.page_content)} chars")
        print()
    
    # Extract topics
    topics = extract_topics(sample_file)
    
    print(f"\\n📋 EXTRACTED {len(topics)} TOPICS:\\n")
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic}")
    
    # Cleanup
    os.remove(sample_file)
    print(f"\\n✓ Demo complete (sample file removed)")


if __name__ == "__main__":
    run_demo()
