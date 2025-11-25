#!/usr/bin/env python3
"""
Professional indexing system for Chrome source code
Handles file discovery, chunking, and batch database insertion
Supports parallel processing and incremental updates
"""

import os
import multiprocessing
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict
from functools import partial

from config import CONFIG
from chunkers import (
    CppChunker, PythonChunker, JavaScriptChunker,
    MojomChunker, GnChunker
)
from utils.logger import (
    get_logger, create_progress_bar,
    print_success, print_error, print_warning, print_header, print_stats
)
from utils.state_manager import StateManager


def process_file_worker(args) -> Tuple[str, str, List, Optional[str]]:
    """
    Worker function for parallel processing
    Must be top-level to be pickleable
    
    Args:
        args: Tuple of (file_path, language, root_path)
        
    Returns:
        Tuple of (file_path, language, chunks, error_message)
    """
    file_path, language, root_path = args
    
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        
        # Skip empty files
        if not code.strip():
            return str(file_path), language, [], None
        
        # Get relative path
        try:
            rel_path = str(Path(file_path).relative_to(root_path))
        except ValueError:
            rel_path = str(file_path)
        
        # Instantiate appropriate chunker
        # We instantiate here to avoid pickling issues with C extensions (tree-sitter)
        chunker = None
        
        # Check if it's a generic tree-sitter language
        file_config = CONFIG.file_types.get(language)
        if file_config and file_config.parser_type == 'treesitter':
            from chunkers import AdaptiveChunker
            # Use AdaptiveChunker with architecture-aware fallback
            chunker = AdaptiveChunker(
                language=language,
                query_scm=file_config.query_scm
            )
        # Fallback to specific chunkers (legacy)
        elif language == 'cpp':
            chunker = CppChunker()
        elif language == 'python':
            chunker = PythonChunker()
        elif language == 'javascript':
            chunker = JavaScriptChunker()
        elif language == 'mojom':
            chunker = MojomChunker()
        elif language == 'gn':
            chunker = GnChunker()
            
        if not chunker:
            return str(file_path), language, [], f"No chunker for language: {language}"
        
        # Extract chunks
        chunks = chunker.extract_chunks(code, rel_path)
        return str(file_path), language, chunks, None
        
    except Exception as e:
        return str(file_path), language, [], str(e)


class ChromeIndexer:
    """
    Professional indexer for Chrome source code
    Discovers files, routes to appropriate chunkers, and manages database insertions
    """
    
    def __init__(self, rag_system):
        self.logger = get_logger()
        self.rag = rag_system
        self.state_manager = StateManager()
        
        # Statistics tracking
        self.stats = {
            'files_processed': 0,
            'files_skipped': 0,
            'files_failed': 0,
            'chunks_created': 0,
            'files_by_type': defaultdict(int),
            'chunks_by_type': defaultdict(int),
            'errors': []
        }
    
    def index_directory(self, source_path: str, file_types: Optional[List[str]] = None,
                       batch_size: Optional[int] = None, parallel: bool = True) -> Dict:
        """
        Index an entire directory tree
        
        Args:
            source_path: Path to Chrome src/ directory
            file_types: Optional filter for specific file types
            batch_size: Optional batch size override
            parallel: Whether to use parallel processing
            
        Returns:
            Dictionary with indexing statistics
        """
        # Reset stats for this run
        self.stats = {
            'files_processed': 0,
            'files_skipped': 0,
            'files_failed': 0,
            'chunks_created': 0,
            'files_by_type': defaultdict(int),
            'chunks_by_type': defaultdict(int),
            'errors': []
        }

        print_header(f"Indexing Chrome Source Code: {source_path}")
        
        source_path = Path(source_path)
        if not source_path.exists():
            print_error(f"Path does not exist: {source_path}")
            return self.stats
        
        batch_size = batch_size or CONFIG.batch_size
        
        # Discover all files
        self.logger.info("Discovering files...")
        all_files = self._discover_files(source_path, file_types)
        
        if not all_files:
            print_warning("No files found to index")
            return self.stats
            
        # Filter files that need processing
        files_to_process = []
        for fp, lang in all_files:
            if self.state_manager.should_process(str(fp)):
                files_to_process.append((fp, lang))
            else:
                self.stats['files_skipped'] += 1
        
        self.logger.info(f"Found {len(all_files)} files ({len(files_to_process)} new/modified, {self.stats['files_skipped']} skipped)")
        
        if not files_to_process:
            print_success("All files are up to date!")
            return self.stats
        
        # Prepare arguments for worker
        worker_args = [(str(fp), lang, str(source_path)) for fp, lang in files_to_process]
        
        # Process files
        with create_progress_bar() as progress:
            task = progress.add_task("[cyan]Processing files...", total=len(files_to_process))
            
            batch = []
            
            # Use multiprocessing if parallel is True and we have enough files
            use_parallel = parallel and len(files_to_process) > 10
            cpu_count = max(1, multiprocessing.cpu_count() - 1)
            
            if use_parallel:
                self.logger.info(f"Starting parallel processing with {cpu_count} workers")
                pool = multiprocessing.Pool(processes=cpu_count)
                iterator = pool.imap_unordered(process_file_worker, worker_args, chunksize=10)
            else:
                self.logger.info("Using sequential processing")
                iterator = map(process_file_worker, worker_args)
            
            try:
                for file_path, language, chunks, error in iterator:
                    if error:
                        self.logger.error(f"Failed to process {file_path}: {error}")
                        self.stats['files_failed'] += 1
                        self.stats['errors'].append(f"{file_path}: {error}")
                    else:
                        # Add to batch
                        batch.extend(chunks)
                        
                        # Update stats
                        self.stats['files_processed'] += 1
                        self.stats['files_by_type'][language] += 1
                        self.stats['chunks_created'] += len(chunks)
                        
                        for chunk in chunks:
                            self.stats['chunks_by_type'][chunk.type] += 1
                        
                        # Mark as processed in state manager
                        self.state_manager.mark_processed(file_path)
                        
                        # Insert batch if it's large enough
                        if len(batch) >= batch_size:
                            self.rag.add_chunks_batch(batch)
                            batch = []
                    
                    progress.update(task, advance=1)
                    
            except KeyboardInterrupt:
                print_warning("\nIndexing interrupted by user")
                if use_parallel:
                    pool.terminate()
                    pool.join()
                return self.stats
            finally:
                if use_parallel:
                    pool.close()
                    pool.join()
            
            # Insert remaining chunks
            if batch:
                self.rag.add_chunks_batch(batch)
        
        # Print final statistics
        print_success(f"Indexing complete!")
        self._print_statistics()
        
        return self.stats
    
    def _discover_files(self, root_path: Path, file_types: Optional[List[str]] = None) -> List[tuple]:
        """
        Recursively discover all supported files
        """
        files = []
        extensions = CONFIG.get_all_extensions()
        
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Filter out excluded directories
            dirnames[:] = [d for d in dirnames if not CONFIG.should_exclude_dir(d)]
            
            for filename in filenames:
                file_path = Path(dirpath) / filename
                ext = file_path.suffix
                
                if ext in extensions:
                    language = CONFIG.get_language_for_extension(ext)
                    
                    # Filter by file type if specified
                    if file_types and language not in file_types:
                        continue
                    
                    files.append((file_path, language))
        
        return files
    
    def _print_statistics(self):
        """Print detailed indexing statistics"""
        stats_dict = {
            "Total Files Scanned": self.stats['files_processed'] + self.stats['files_skipped'] + self.stats['files_failed'],
            "Files Processed": self.stats['files_processed'],
            "Files Skipped (Up-to-date)": self.stats['files_skipped'],
            "Files Failed": self.stats['files_failed'],
            "Total Chunks Created": self.stats['chunks_created'],
        }
        
        if self.stats['files_processed'] > 0:
            stats_dict["Avg Chunks/File"] = f"{self.stats['chunks_created'] / self.stats['files_processed']:.2f}"
        
        # Add files by type
        for lang, count in self.stats['files_by_type'].items():
            stats_dict[f"Files ({lang})"] = count
        
        print_stats(stats_dict)
        
        # Log errors if any
        if self.stats['errors']:
            print_warning(f"Encountered {len(self.stats['errors'])} errors")
            for error in self.stats['errors'][:5]:
                self.logger.error(error)
