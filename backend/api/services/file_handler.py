# backend/api/services/file_handler.py

"""
File handling service for temporary uploads.
Manages saving, cleanup, and validation of uploaded files.
"""

import os
import uuid
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from fastapi import UploadFile
import aiofiles

from ..config import settings


class FileHandler:
    """
    Handles temporary file storage for uploads.
    
    Features:
    - Async file operations
    - Automatic cleanup of old files
    - Unique filename generation
    """
    
    def __init__(self):
        """Initialize file handler and ensure temp directory exists."""
        self.temp_dir = settings.temp_upload_dir
        self.max_age_hours = settings.TEMP_FILE_MAX_AGE_HOURS
    
    async def save_upload(
        self, 
        file: UploadFile, 
        content: bytes
    ) -> Path:
        """
        Save an uploaded file to temporary storage.
        
        Args:
            file: The uploaded file
            content: File content as bytes (already read)
        
        Returns:
            Path to the saved temporary file
        """
        # Generate unique filename
        file_ext = Path(file.filename).suffix if file.filename else ".pdf"
        unique_name = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
        temp_path = self.temp_dir / unique_name
        
        # Write file asynchronously
        async with aiofiles.open(temp_path, 'wb') as f:
            await f.write(content)
        
        return temp_path
    
    async def cleanup_file(self, file_path: Path) -> bool:
        """
        Delete a temporary file.
        
        Args:
            file_path: Path to the file to delete
        
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if file_path.exists():
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Warning: Failed to cleanup temp file {file_path}: {e}")
            return False
    
    async def cleanup_old_files(self) -> int:
        """
        Remove temporary files older than max_age_hours.
        
        Returns:
            Number of files cleaned up
        """
        cleaned = 0
        cutoff_time = datetime.now() - timedelta(hours=self.max_age_hours)
        
        try:
            for file_path in self.temp_dir.iterdir():
                if file_path.is_file():
                    # Check file modification time
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff_time:
                        os.remove(file_path)
                        cleaned += 1
        except Exception as e:
            print(f"Warning: Error during temp file cleanup: {e}")
        
        return cleaned
    
    def get_temp_file_count(self) -> int:
        """Get count of files in temp directory."""
        try:
            return sum(1 for f in self.temp_dir.iterdir() if f.is_file())
        except Exception:
            return 0
    
    def validate_file_type(self, filename: str) -> bool:
        """
        Validate file extension against allowed types.
        
        Args:
            filename: Original filename with extension
        
        Returns:
            True if file type is allowed
        """
        if not filename:
            return False
        ext = Path(filename).suffix.lower()
        return ext in settings.allowed_extensions_list
    
    def validate_file_size(self, size_bytes: int) -> bool:
        """
        Validate file size against maximum.
        
        Args:
            size_bytes: File size in bytes
        
        Returns:
            True if file size is within limits
        """
        return size_bytes <= settings.max_file_size_bytes


# Singleton instance
_file_handler: Optional[FileHandler] = None


def get_file_handler() -> FileHandler:
    """Get or create the FileHandler singleton."""
    global _file_handler
    if _file_handler is None:
        _file_handler = FileHandler()
    return _file_handler
