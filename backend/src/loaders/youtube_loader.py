# backend/src/loaders/youtube_loader.py

"""
YouTube Loader Module

Fetches YouTube video transcripts and converts them to LangChain Documents.
Uses the youtube-transcript-api library to extract transcripts.
"""

from typing import List, Optional
from langchain_core.documents import Document
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from langchain_core.documents import Document
import re


class YouTubeLoader:
    """Load YouTube video transcripts as LangChain Documents."""
    
    def __init__(self):
        """Initialize YouTube loader."""
        pass
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats.
        
        Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID (11 characters) or None if not found
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
            r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                # YouTube video IDs are exactly 11 characters
                return video_id[:11]
        
        return None
    
    def load_transcript(self, url: str) -> List[Document]:
        """
        Load transcript from YouTube video URL.
        
        Args:
            url: YouTube video URL
            
        Returns:
            List containing a single Document with the transcript
        """
        print(f"\n{'─'*60}")
        print(f"🎥 LOADING YOUTUBE VIDEO")
        print(f"{'─'*60}")
        print(f"   URL: {url}")
        
        # Extract video ID
        video_id = self.extract_video_id(url)
        
        if not video_id:
            print(f"   ✗ Invalid YouTube URL")
            print(f"   Expected format: https://www.youtube.com/watch?v=VIDEO_ID")
            return []
        
        print(f"   Video ID: {video_id}")
        
        # Fetch transcript
        try:
            print(f"   📡 Fetching transcript...")
            
            # Use the instance-based API
            api = YouTubeTranscriptApi()
            
            # Get available transcripts
            try:
                transcript_list = api.list(video_id)
                
                # Convert to list if needed and get first transcript
                if hasattr(transcript_list, '__iter__'):
                    transcript_obj = None
                    for t in transcript_list:
                        transcript_obj = t
                        break
                    
                    if transcript_obj:
                        # Fetch the actual transcript data
                        transcript_data = transcript_obj.fetch()
                        print(f"   ✓ Fetched transcript ({len(transcript_data)} segments)")
                    else:
                        print(f"   ✗ No transcript available")
                        print(f"{'─'*60}")
                        return []
                else:
                    print(f"   ✗ Could not list transcripts")
                    print(f"{'─'*60}")
                    return []
                    
            except Exception as e:
                print(f"   ✗ Error listing transcripts: {str(e)}")
                print(f"   💡 Tip: Make sure the video has captions enabled")
                print(f"{'─'*60}")
                return []
            
            # Combine all transcript segments
            full_text = " ".join([entry['text'] for entry in transcript_data])
            
            # Clean up transcript
            full_text = re.sub(r'\s+', ' ', full_text)  # Normalize whitespace
            full_text = full_text.strip()
            
            if not full_text or len(full_text) < 100:
                print(f"   ⚠ Transcript too short ({len(full_text)} chars)")
                return []
            
            print(f"   ✓ Loaded transcript: {len(full_text)} characters")
            print(f"   ✓ Duration: {len(transcript_data)} segments")
            print(f"{'─'*60}")
            
            # Create LangChain Document
            doc = Document(
                page_content=full_text,
                metadata={
                    "source": url,
                    "type": "youtube",
                    "video_id": video_id,
                    "length": len(full_text),
                    "segments": len(transcript_list)
                }
            )
            
            return [doc]
            
        except TranscriptsDisabled:
            print(f"   ✗ Transcripts are disabled for this video")
            print(f"{'─'*60}")
            return []
        
        except NoTranscriptFound:
            print(f"   ✗ No transcript found (video may not have captions)")
            print(f"{'─'*60}")
            return []
        
        except VideoUnavailable:
            print(f"   ✗ Video unavailable (may be private or deleted)")
            print(f"{'─'*60}")
            return []
        
        except Exception as e:
            print(f"   ✗ Error loading transcript: {str(e)}")
            print(f"   💡 Tip: Make sure the video has captions/subtitles enabled")
            print(f"{'─'*60}")
            return []


# Convenience function for quick usage
def load_youtube_video(url: str) -> List[Document]:
    """
    Quick function to load YouTube video transcript.
    
    Args:
        url: YouTube video URL
        
    Returns:
        List of Documents
    """
    loader = YouTubeLoader()
    return loader.load_transcript(url)
