# backend/src/loaders/__init__.py

"""
Rooster-HackCrypt: Content Loaders

This module provides loaders for various content types:
- YouTube videos (transcript-based)
- Syllabus topics (LLM-generated educational content)
- PDFs (handled by DocumentProcessor)
"""

from .youtube_loader import YouTubeLoader
from .syllabus_loader import SyllabusLoader

__all__ = ['YouTubeLoader', 'SyllabusLoader']
