# backend/src/rag/url_loader.py

"""
URL Content Loader Module

Fetches content from URLs and converts it to documents for indexing.
Supports:
- Plain web pages (HTML)
- Articles and blog posts
- Documentation pages
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from langchain_core.documents import Document
import time


class URLLoader:
    """Load and parse content from URLs."""
    
    def __init__(self, timeout: int = 30, user_agent: Optional[str] = None):
        """
        Initialize URL loader.
        
        Args:
            timeout: Request timeout in seconds
            user_agent: Custom user agent string
        """
        self.timeout = timeout
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
    
    def fetch_url(self, url: str) -> Optional[str]:
        """
        Fetch content from a URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content or None if failed
        """
        try:
            print(f"   📡 Fetching: {url}")
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            print(f"   ✓ Fetched {len(response.text)} characters")
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"   ✗ Failed to fetch {url}: {str(e)}")
            return None
    
    def extract_text(self, html: str, url: str) -> Optional[Document]:
        """
        Extract clean text from HTML.
        
        Args:
            html: Raw HTML content
            url: Source URL (for metadata)
            
        Returns:
            Document with extracted text
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            if not text or len(text) < 100:
                print(f"   ⚠ Extracted text too short ({len(text)} chars)")
                return None
            
            # Get title
            title = soup.find('title')
            title_text = title.string if title else url
            
            doc = Document(
                page_content=text,
                metadata={
                    "source": url,
                    "title": title_text,
                    "type": "url",
                    "length": len(text)
                }
            )
            
            print(f"   ✓ Extracted {len(text)} characters")
            return doc
            
        except Exception as e:
            print(f"   ✗ Failed to extract text: {str(e)}")
            return None
    
    def load_url(self, url: str) -> Optional[Document]:
        """
        Load and parse a single URL.
        
        Args:
            url: URL to load
            
        Returns:
            Document with content
        """
        html = self.fetch_url(url)
        if not html:
            return None
        
        return self.extract_text(html, url)
    
    def load_urls(self, urls: List[str], delay: float = 1.0) -> List[Document]:
        """
        Load multiple URLs with rate limiting.
        
        Args:
            urls: List of URLs to load
            delay: Delay between requests (seconds)
            
        Returns:
            List of documents
        """
        docs = []
        
        print(f"\n{'─'*60}")
        print(f"📡 LOADING {len(urls)} URLS")
        print(f"{'─'*60}")
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] {url}")
            
            doc = self.load_url(url)
            if doc:
                docs.append(doc)
            
            # Rate limiting
            if i < len(urls):
                time.sleep(delay)
        
        print(f"\n{'─'*60}")
        print(f"✓ Successfully loaded {len(docs)}/{len(urls)} URLs")
        print(f"{'─'*60}")
        
        return docs


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def load_url(url: str, timeout: int = 30) -> Optional[Document]:
    """
    Load a single URL.
    
    Args:
        url: URL to load
        timeout: Request timeout
        
    Returns:
        Document or None
    """
    loader = URLLoader(timeout=timeout)
    return loader.load_url(url)


def load_urls(urls: List[str], timeout: int = 30, delay: float = 1.0) -> List[Document]:
    """
    Load multiple URLs.
    
    Args:
        urls: List of URLs
        timeout: Request timeout
        delay: Delay between requests
        
    Returns:
        List of documents
    """
    loader = URLLoader(timeout=timeout)
    return loader.load_urls(urls, delay=delay)


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════════════════════

def run_demo():
    """Demo URL loading."""
    print("\n🌐 URL LOADER DEMO\n")
    
    # Example URLs
    test_urls = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Machine_learning"
    ]
    
    docs = load_urls(test_urls, delay=2.0)
    
    print(f"\n📊 RESULTS:")
    for i, doc in enumerate(docs, 1):
        print(f"\n{i}. {doc.metadata['title']}")
        print(f"   Source: {doc.metadata['source']}")
        print(f"   Length: {doc.metadata['length']} chars")
        print(f"   Preview: {doc.page_content[:200]}...")


if __name__ == "__main__":
    run_demo()
