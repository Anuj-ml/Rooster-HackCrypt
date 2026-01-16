# backend/src/loaders/syllabus_loader.py

"""
Syllabus Loader Module

Generates comprehensive educational content for syllabus topics using Groq LLM.
Acts as a "textbook writer" to create detailed study material.
"""

from typing import List
from langchain_core.documents import Document


class SyllabusLoader:
    """Generate educational content for syllabus topics using LLM."""
    
    def __init__(self, llm):
        """
        Initialize syllabus loader.
        
        Args:
            llm: LangChain LLM instance (e.g., ChatGroq)
        """
        self.llm = llm
    
    def generate_content(self, topic: str) -> List[Document]:
        """
        Generate comprehensive educational content for a topic.
        
        Args:
            topic: Syllabus topic to generate content for
            
        Returns:
            List containing a single Document with generated content
        """
        print(f"\n{'─'*60}")
        print(f"📚 GENERATING SYLLABUS CONTENT")
        print(f"{'─'*60}")
        print(f"   Topic: {topic}")
        
        # Create the prompt
        prompt = f"""You are a professor writing a comprehensive textbook chapter.

Topic: {topic}

Write a detailed, factual, and educational chapter covering this topic. Include:

1. **Introduction**: Overview and importance of the topic
2. **Key Concepts**: Core principles and definitions
3. **Detailed Explanation**: In-depth coverage of the subject matter
4. **Examples**: Practical examples and applications
5. **Important Points**: Critical facts and relationships
6. **Summary**: Key takeaways

Requirements:
- Write in clear, academic language
- Provide specific facts and details
- Include relevant terminology
- Make it comprehensive and self-contained
- Aim for at least 1500-2000 words
- Do NOT include markdown headers or special formatting
- Write as continuous prose

Begin writing the chapter now:"""
        
        try:
            print(f"   🤖 Generating content with Groq LLM...")
            
            # Invoke the LLM
            response = self.llm.invoke(prompt)
            
            # Extract content
            content = response.content if hasattr(response, 'content') else str(response)
            
            if not content or len(content) < 500:
                print(f"   ⚠ Generated content too short ({len(content)} chars)")
                print(f"   ✗ Failed to generate adequate content")
                print(f"{'─'*60}")
                return []
            
            print(f"   ✓ Generated {len(content)} characters")
            print(f"   ✓ Content ready for indexing")
            print(f"{'─'*60}")
            
            # Create LangChain Document
            doc = Document(
                page_content=content,
                metadata={
                    "source": "syllabus",
                    "type": "syllabus",
                    "topic": topic,
                    "length": len(content),
                    "generated": True
                }
            )
            
            return [doc]
            
        except Exception as e:
            print(f"   ✗ Error generating content: {str(e)}")
            print(f"{'─'*60}")
            return []


# Convenience function for quick usage
def generate_syllabus_content(llm, topic: str) -> List[Document]:
    """
    Quick function to generate syllabus content.
    
    Args:
        llm: LangChain LLM instance
        topic: Topic to generate content for
        
    Returns:
        List of Documents
    """
    loader = SyllabusLoader(llm)
    return loader.generate_content(topic)
