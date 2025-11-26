#!/usr/bin/env python3
"""
Chrome Source Code RAG System - Refactored
Professional vector database management for Chrome source code
"""

from typing import List, Dict, Optional
from collections import defaultdict
import chromadb
from chromadb.utils import embedding_functions

from chunkers.base_chunker import CodeChunk
from config import CONFIG
from utils.logger import get_logger


from rank_bm25 import BM25Okapi
import numpy as np

class ChromeRAGSystem:
    """
    Professional RAG system for Chrome source code
    Manages vector database operations with efficient batch processing
    """
    
    def __init__(self, db_path: Optional[str] = None, collection_name: Optional[str] = None):
        """
        Initialize the RAG system
        
        Args:
            db_path: Path to ChromaDB storage
            collection_name: Name of the collection to use
        """
        self.logger = get_logger()
        self.db_path = db_path or CONFIG.db_path
        self.collection_name = collection_name or CONFIG.collection_name
        
        # Initialize ChromaDB
        self.logger.info(f"Initializing ChromaDB at {self.db_path}")
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Use default embedding function
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn,
            metadata={"description": "Chrome source code for vulnerability analysis"}
        )
        
        self.logger.info(f"Collection '{self.collection_name}' ready")
        self._chunk_counter = self.collection.count()
        
        # Initialize BM25 index
        self.bm25 = None
        self.bm25_corpus = []
        self.bm25_ids = []
        self.bm25_metadatas = []
        self._build_keyword_index()
    
    def _build_keyword_index(self):
        """Build BM25 index from existing documents in ChromaDB"""
        self.logger.info("Building BM25 keyword index...")
        try:
            # Fetch all documents (this might be heavy for very large datasets)
            # For production, we might want to cache this or load incrementally
            all_docs = self.collection.get()
            
            if not all_docs['ids']:
                self.logger.info("No documents to index for BM25")
                return
            
            self.bm25_ids = all_docs['ids']
            self.bm25_metadatas = all_docs['metadatas']
            
            # Tokenize documents for BM25
            tokenized_corpus = [doc.lower().split() for doc in all_docs['documents']]
            self.bm25 = BM25Okapi(tokenized_corpus)
            self.logger.info(f"BM25 index built with {len(self.bm25_ids)} documents")
            
        except Exception as e:
            self.logger.error(f"Failed to build BM25 index: {e}")

    def add_chunks_batch(self, chunks: List[CodeChunk]) -> int:
        """
        Add multiple chunks in a single batch operation
        
        Args:
            chunks: List of CodeChunk objects
            
        Returns:
            Number of chunks added
        """
        if not chunks:
            return 0
        
        ids = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            chunk_id = f"chunk_{self._chunk_counter}"
            self._chunk_counter += 1
            
            ids.append(chunk_id)
            documents.append(chunk.content)
            metadatas.append(chunk.to_dict())
        
        # Batch insert
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        # Update BM25 index (incremental update is tricky with BM25Okapi, 
        # so we'll just rebuild it for now or append if possible, but rebuilding is safer for consistency)
        # For performance, we might want to defer this until after a large batch import
        # But for now, let's keep it simple and rebuild
        # self._build_keyword_index() # Commented out for performance during bulk index
        
        return len(chunks)
    
    def retrieve_symbol(self, symbol_name: str, symbol_type: Optional[str] = None,
                       language: Optional[str] = None, n_results: int = 5) -> List[Dict]:
        """
        Retrieve specific symbol by name
        
        Args:
            symbol_name: Name of the symbol to find
            symbol_type: Optional type filter (function, class, etc.)
            language: Optional language filter (cpp, python, etc.)
            n_results: Maximum number of results
            
        Returns:
            List of matching chunks with metadata
        """
        conditions = [{"name": symbol_name}]
        
        if symbol_type:
            conditions.append({"type": symbol_type})
        
        if language:
            conditions.append({"language": language})
            
        where_clause = {"$and": conditions} if len(conditions) > 1 else conditions[0]
        
        try:
            results = self.collection.get(
                where=where_clause,
                limit=n_results
            )
            return self._format_get_results(results)
        except Exception as e:
            self.logger.error(f"Error retrieving symbol: {e}")
            return []
    
    def retrieve_context(self, query: str, n_results: int = 5,
                        language: Optional[str] = None,
                        file_type: Optional[str] = None) -> List[Dict]:
        """
        Hybrid Semantic Search (Vector + BM25)
        
        Args:
            query: Search query
            n_results: Number of results to return
            language: Optional language filter
            file_type: Optional file type filter
            
        Returns:
            List of relevant chunks with metadata and similarity scores
        """
        # 1. Vector Search
        vector_results = []
        
        conditions = []
        if language:
            conditions.append({"language": language})
        if file_type:
            conditions.append({"type": file_type})
            
        where_clause = {}
        if len(conditions) > 1:
            where_clause = {"$and": conditions}
        elif len(conditions) == 1:
            where_clause = conditions[0]
            
        try:
            v_res = self.collection.query(
                query_texts=[query],
                n_results=n_results * 2, # Fetch more for re-ranking
                where=where_clause if where_clause else None
            )
            vector_results = self._format_query_results(v_res)
        except Exception as e:
            self.logger.error(f"Vector search failed: {e}")

        # 2. Keyword Search (BM25)
        keyword_results = []
        if self.bm25:
            try:
                tokenized_query = query.lower().split()
                # Get top N documents
                doc_scores = self.bm25.get_scores(tokenized_query)
                top_n_indices = np.argsort(doc_scores)[::-1][:n_results * 2]
                
                for idx in top_n_indices:
                    if doc_scores[idx] > 0:
                        # Apply filters manually since BM25 doesn't support them natively
                        metadata = self.bm25_metadatas[idx]
                        if language and metadata.get('language') != language:
                            continue
                        if file_type and metadata.get('type') != file_type:
                            continue
                            
                        keyword_results.append({
                            'content': "Content not stored in RAM", # We don't store content in RAM to save space
                            'metadata': metadata,
                            'id': self.bm25_ids[idx],
                            'score': doc_scores[idx]
                        })
            except Exception as e:
                self.logger.error(f"Keyword search failed: {e}")
        
        # 3. Reciprocal Rank Fusion (RRF)
        combined_results = self._rrf_fusion(vector_results, keyword_results, k=60)
        
        # Fill in content for keyword results if missing (from vector results or DB)
        # Since we need to return content, we might need to fetch it if it came purely from BM25
        # But for simplicity, let's assume we can get it. 
        # Actually, let's just return the top N combined
        
        final_results = combined_results[:n_results]
        
        # Fetch content for any result that doesn't have it (BM25 hits not in Vector hits)
        ids_to_fetch = [r['id'] for r in final_results if 'content' not in r or r['content'] == "Content not stored in RAM"]
        if ids_to_fetch:
            fetched = self.collection.get(ids=ids_to_fetch)
            id_map = {id: (doc, meta) for id, doc, meta in zip(fetched['ids'], fetched['documents'], fetched['metadatas'])}
            
            for r in final_results:
                if r['id'] in id_map:
                    r['content'] = id_map[r['id']][0]
                    r['metadata'] = id_map[r['id']][1]
                    
        return final_results

    def _rrf_fusion(self, vector_results: List[Dict], keyword_results: List[Dict], k: int = 60) -> List[Dict]:
        """
        Combine results using Reciprocal Rank Fusion
        score = 1 / (k + rank)
        """
        scores = defaultdict(float)
        
        # Process Vector Results
        for rank, result in enumerate(vector_results):
            scores[result['id']] += 1 / (k + rank + 1)
            
        # Process Keyword Results
        for rank, result in enumerate(keyword_results):
            scores[result['id']] += 1 / (k + rank + 1)
            
        # Sort by combined score
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        # Create final list merging data
        merged = []
        seen_ids = set()
        
        # Create a map for quick lookup
        all_results_map = {r['id']: r for r in vector_results + keyword_results}
        
        for doc_id in sorted_ids:
            if doc_id in all_results_map:
                result = all_results_map[doc_id]
                result['rrf_score'] = scores[doc_id]
                merged.append(result)
        
        return merged

    def get_statistics(self) -> Dict:
        """
        Get comprehensive database statistics
        
        Returns:
            Dictionary with statistics about indexed code
        """
        total_chunks = self.collection.count()
        
        # Get sample to analyze distribution
        sample_size = min(1000, total_chunks)
        if sample_size == 0:
            return {
                'total_chunks': 0,
                'chunks_by_type': {},
                'chunks_by_language': {},
                'unique_files': 0
            }
        
        # Get all metadata (this could be slow for large collections)
        all_data = self.collection.get(limit=sample_size)
        
        stats = {
            'total_chunks': total_chunks,
            'chunks_by_type': defaultdict(int),
            'chunks_by_language': defaultdict(int),
            'files': set()
        }
        
        if all_data and 'metadatas' in all_data:
            for metadata in all_data['metadatas']:
                stats['chunks_by_type'][metadata.get('type', 'unknown')] += 1
                stats['chunks_by_language'][metadata.get('language', 'unknown')] += 1
                stats['files'].add(metadata.get('filepath', ''))
        
        stats['unique_files'] = len(stats['files'])
        del stats['files']  # Don't include the set in return
        
        # Convert defaultdicts to regular dicts
        stats['chunks_by_type'] = dict(stats['chunks_by_type'])
        stats['chunks_by_language'] = dict(stats['chunks_by_language'])
        
        return stats
    
    def clear_collection(self):
        """Delete and recreate the collection"""
        self.logger.warning(f"Deleting collection '{self.collection_name}'")
        self.client.delete_collection(self.collection_name)
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn
        )
        
        self._chunk_counter = 0
        self.bm25 = None # Reset BM25
        self.logger.info("Collection cleared and recreated")
    
    def _format_get_results(self, results: Dict) -> List[Dict]:
        """Format results from get() operation"""
        formatted = []
        
        if results and 'documents' in results:
            for i, doc in enumerate(results['documents']):
                formatted.append({
                    'content': doc,
                    'metadata': results['metadatas'][i] if results['metadatas'] else {},
                    'id': results['ids'][i] if results['ids'] else None
                })
        
        return formatted
    
    def _format_query_results(self, results: Dict) -> List[Dict]:
        """Format results from query() operation"""
        formatted = []
        
        if results and 'documents' in results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                formatted.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else None,
                    'id': results['ids'][0][i] if results['ids'] else None
                })
        
        return formatted


class VulnerabilityAnalyzer:
    """
    Template class for AI-driven vulnerability analysis
    This is a framework - integrate with your preferred AI API
    """
    
    def __init__(self, rag_system: ChromeRAGSystem):
        self.rag = rag_system
        self.logger = get_logger()
    
    async def analyze_file(self, filepath: str) -> Dict:
        """
        Analyze a file for vulnerabilities with RAG support
        
        This is a template method - you'll need to integrate with your AI API
        (e.g., OpenAI, Anthropic, Google AI, etc.)
        
        Args:
            filepath: Path to file to analyze
            
        Returns:
            Dictionary with analysis results
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        self.logger.info(f"Analyzing {filepath}")
        
        # Step 1: Get initial context from RAG
        filename = filepath.split('/')[-1]
        context_chunks = self.rag.retrieve_context(
            f"security vulnerabilities in {filename}",
            n_results=3
        )
        
        # Step 2: Build prompt with context
        context_text = "\n\n".join([
            f"// Related code from {chunk['metadata']['filepath']}\n{chunk['content']}"
            for chunk in context_chunks
        ])
        
        prompt = f"""Analyze this code for security vulnerabilities:

FILE: {filepath}
{code}

RELATED CODE CONTEXT:
{context_text}

Please identify any potential security issues."""
        
        # TODO: Send to your AI API
        # response = await your_ai_api.complete(prompt)
        
        return {
            'filepath': filepath,
            'prompt_length': len(prompt),
            'context_chunks_used': len(context_chunks),
            'vulnerabilities': []  # Parse from AI response
        }