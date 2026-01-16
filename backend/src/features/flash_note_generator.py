"""
Flash-Note Generator Feature

Instantly generates cheat sheets of atomic facts for any topic without using LLM tokens.
Retrieves propositions directly from ChromaDB based on semantic similarity.
"""

from typing import List, Optional, Dict


class FlashNoteGenerator:
    """
    Zero-cost flash note generator that retrieves stored propositions.
    
    Unlike quiz generation, this feature:
    - Does NOT use any LLM tokens
    - Returns raw propositions directly from ChromaDB
    - Formats them as a clean cheat sheet
    """
    
    def __init__(self, knowledge_base):
        """
        Initialize with knowledge base for retrieval.
        
        Args:
            knowledge_base: KnowledgeBase instance with ChromaDB access
        """
        self.kb = knowledge_base
    
    def generate_cheat_sheet(
        self, 
        topic: str, 
        source_id: Optional[str] = None,
        num_facts: int = 20
    ) -> Dict[str, any]:
        """
        Generate a cheat sheet of atomic facts for a topic.
        
        Args:
            topic: The topic to generate facts about
            source_id: Optional PDF source ID to filter results
            num_facts: Number of facts to retrieve (default: 20, max: 50)
            
        Returns:
            Dictionary with topic, fact_count, and cheat_sheet list
        """
        # Limit max facts to prevent overwhelming response
        num_facts = min(num_facts, 50)
        
        # Retrieve raw propositions from storage
        propositions = self.kb.get_raw_propositions(
            query=topic,
            pdf_source_id=source_id,
            k=num_facts
        )
        
        if not propositions:
            return {
                "topic": topic,
                "fact_count": 0,
                "cheat_sheet": [],
                "message": f"No facts found for topic '{topic}'" + 
                          (f" in source '{source_id}'" if source_id else "")
            }
        
        # Format propositions as bullet points
        formatted_facts = [f"• {fact}" for fact in propositions]
        
        return {
            "topic": topic,
            "fact_count": len(formatted_facts),
            "cheat_sheet": formatted_facts,
            "source_id": source_id
        }
    
    def generate_cheat_sheet_by_source(
        self,
        source_id: str,
        num_facts: int = 30
    ) -> Dict[str, any]:
        """
        Generate a comprehensive cheat sheet from an entire source.
        
        Args:
            source_id: PDF source ID to generate facts from
            num_facts: Number of facts to retrieve (default: 30)
            
        Returns:
            Dictionary with source_id, fact_count, and cheat_sheet list
        """
        # Use "default" query to get random facts from entire source
        return self.generate_cheat_sheet(
            topic="default",
            source_id=source_id,
            num_facts=num_facts
        )
