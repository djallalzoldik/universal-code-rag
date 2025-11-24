#!/usr/bin/env python3
"""
State manager for incremental indexing
Tracks file modification times and hashes to skip unchanged files
"""

import sqlite3
import hashlib
import os
from pathlib import Path
from typing import Optional, Tuple, Set
from .logger import get_logger

class StateManager:
    """
    Manages the indexing state database (SQLite)
    Tracks which files have been indexed and their last modification time/hash
    """
    
    def __init__(self, db_path: str = "index_state.db"):
        self.db_path = db_path
        self.logger = get_logger()
        self._init_db()
        
    def _init_db(self):
        """Initialize the SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS files (
                        filepath TEXT PRIMARY KEY,
                        mtime REAL,
                        file_hash TEXT,
                        last_indexed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
        except Exception as e:
            self.logger.error(f"Failed to initialize state database: {e}")

    def should_process(self, filepath: str) -> bool:
        """
        Check if a file needs to be processed
        Returns True if file is new or modified since last index
        """
        try:
            path = Path(filepath)
            if not path.exists():
                return False
                
            current_mtime = path.stat().st_mtime
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT mtime FROM files WHERE filepath = ?", 
                    (str(filepath),)
                )
                row = cursor.fetchone()
                
                if row is None:
                    return True  # New file
                
                last_mtime = row[0]
                return current_mtime > last_mtime
                
        except Exception as e:
            self.logger.warning(f"Error checking state for {filepath}: {e}")
            return True  # Process on error to be safe

    def mark_processed(self, filepath: str):
        """Mark a file as successfully processed"""
        try:
            path = Path(filepath)
            current_mtime = path.stat().st_mtime
            
            # Calculate simple hash for verification (optional, can be slow for large files)
            # For now relying on mtime is faster and usually sufficient
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO files (filepath, mtime, last_indexed)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (str(filepath), current_mtime))
                
        except Exception as e:
            self.logger.error(f"Failed to update state for {filepath}: {e}")

    def get_all_indexed_files(self) -> Set[str]:
        """Get set of all currently indexed file paths"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT filepath FROM files")
                return {row[0] for row in cursor.fetchall()}
        except Exception:
            return set()

    def remove_file(self, filepath: str):
        """Remove a file from state (e.g. if deleted)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM files WHERE filepath = ?", (str(filepath),))
        except Exception as e:
            self.logger.error(f"Failed to remove state for {filepath}: {e}")

    def clear(self):
        """Clear all state"""
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            self._init_db()
        except Exception as e:
            self.logger.error(f"Failed to clear state: {e}")
