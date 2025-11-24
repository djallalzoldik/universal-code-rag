#!/usr/bin/env python3
"""
Comprehensive CLI for Chrome RAG System
Command-line interface for indexing, searching, and managing the vector database
"""

import argparse
import sys
from pathlib import Path

from rag import ChromeRAGSystem, VulnerabilityAnalyzer
from indexer import ChromeIndexer
from config import CONFIG
from utils.logger import (
    setup_logger, print_success, print_error, print_warning,
    print_header, print_stats, console
)
from rich.table import Table
from rich.syntax import Syntax


def cmd_index(args):
    """Index a Chrome source directory"""
    print_header("Chrome Source Code Indexer")
    
    # Validate path
    source_path = Path(args.path)
    if not source_path.exists():
        print_error(f"Path does not exist: {source_path}")
        return 1
    
    if not source_path.is_dir():
        print_error(f"Path is not a directory: {source_path}")
        return 1
    
    # Initialize systems
    rag = ChromeRAGSystem(db_path=args.db_path)
    indexer = ChromeIndexer(rag)
    
    # Optionally clear existing data
    if args.clear:
        print_warning("Clearing existing database...")
        rag.clear_collection()
        indexer.state_manager.clear()
    elif args.force:
        print_warning("Forcing re-index (clearing state)...")
        indexer.state_manager.clear()
    
    # Parse file types filter
    file_types = args.file_types.split(',') if args.file_types else None
    
    # Index directory
    stats = indexer.index_directory(
        source_path=str(source_path),
        file_types=file_types,
        batch_size=args.batch_size,
        parallel=not args.no_parallel
    )
    
    return 0


def cmd_search(args):
    """Semantic search for code chunks"""
    print_header("Semantic Code Search")
    
    # Initialize RAG system
    rag = ChromeRAGSystem(db_path=args.db_path)
    
    # Perform search
    results = rag.retrieve_context(
        query=args.query,
        n_results=args.n_results,
        language=args.language,
        file_type=args.type
    )
    
    if not results:
        print_warning("No results found")
        return 0
    
    print_success(f"Found {len(results)} results\n")
    
    # Display results
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        
        console.print(f"\n[bold cyan]Result {i}[/bold cyan]")
        console.print(f"[yellow]File:[/yellow] {metadata.get('filepath', 'unknown')}")
        console.print(f"[yellow]Type:[/yellow] {metadata.get('type', 'unknown')}")
        console.print(f"[yellow]Name:[/yellow] {metadata.get('name', 'unknown')}")
        console.print(f"[yellow]Language:[/yellow] {metadata.get('language', 'unknown')}")
        console.print(f"[yellow]Lines:[/yellow] {metadata.get('line_start', '?')}-{metadata.get('line_end', '?')}")
        
        if result.get('distance') is not None:
            console.print(f"[yellow]Similarity:[/yellow] {1 - result['distance']:.3f}")
        
        # Show code snippet
        content = result['content']
        if len(content) > 500 and not args.full:
            content = content[:500] + "\n... (truncated, use --full to see complete code)"
        
        # Syntax highlight the code
        language_map = {
            'cpp': 'cpp',
            'python': 'python',
            'javascript': 'javascript',
            'mojom': 'rust',  # Similar syntax
            'gn': 'python'    # Similar syntax
        }
        syntax_lang = language_map.get(metadata.get('language'), 'text')
        
        syntax = Syntax(content, syntax_lang, theme="monokai", line_numbers=True)
        console.print(syntax)
        console.print("[dim]" + "─" * 80 + "[/dim]")
    
    return 0


def cmd_symbol(args):
    """Retrieve specific symbol by name"""
    print_header("Symbol Lookup")
    
    # Initialize RAG system
    rag = ChromeRAGSystem(db_path=args.db_path)
    
    # Retrieve symbol
    results = rag.retrieve_symbol(
        symbol_name=args.name,
        symbol_type=args.type,
        language=args.language,
        n_results=args.n_results
    )
    
    if not results:
        print_warning(f"Symbol '{args.name}' not found")
        return 0
    
    print_success(f"Found {len(results)} definition(s) of '{args.name}'\n")
    
    # Display results
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        
        console.print(f"\n[bold cyan]Definition {i}[/bold cyan]")
        console.print(f"[yellow]File:[/yellow] {metadata.get('filepath', 'unknown')}")
        console.print(f"[yellow]Type:[/yellow] {metadata.get('type', 'unknown')}")
        console.print(f"[yellow]Language:[/yellow] {metadata.get('language', 'unknown')}")
        console.print(f"[yellow]Lines:[/yellow] {metadata.get('line_start', '?')}-{metadata.get('line_end', '?')}")
        
        if metadata.get('signature'):
            console.print(f"[yellow]Signature:[/yellow] {metadata['signature']}")
        
        if metadata.get('namespace'):
            console.print(f"[yellow]Namespace:[/yellow] {metadata['namespace']}")
        
        # Show code
        content = result['content']
        language_map = {
            'cpp': 'cpp',
            'python': 'python',
            'javascript': 'javascript',
            'mojom': 'rust',
            'gn': 'python'
        }
        syntax_lang = language_map.get(metadata.get('language'), 'text')
        
        syntax = Syntax(content, syntax_lang, theme="monokai", line_numbers=True)
        console.print(syntax)
        console.print("[dim]" + "─" * 80 + "[/dim]")
    
    return 0


def cmd_stats(args):
    """Display database statistics"""
    print_header("Database Statistics")
    
    # Initialize RAG system
    rag = ChromeRAGSystem(db_path=args.db_path)
    
    # Get statistics
    stats = rag.get_statistics()
    
    # Create main stats table
    main_stats = {
        "Total Chunks": stats['total_chunks'],
        "Unique Files": stats['unique_files']
    }
    print_stats(main_stats)
    
    # Create chunks by type table
    if stats['chunks_by_type']:
        console.print()
        type_table = Table(title="Chunks by Type", show_header=True, header_style="bold magenta")
        type_table.add_column("Type", style="cyan", no_wrap=True)
        type_table.add_column("Count", style="green", justify="right")
        type_table.add_column("Percentage", style="yellow", justify="right")
        
        total = stats['total_chunks']
        for chunk_type, count in sorted(stats['chunks_by_type'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            type_table.add_row(chunk_type, str(count), f"{percentage:.1f}%")
        
        console.print(type_table)
    
    # Create chunks by language table
    if stats['chunks_by_language']:
        console.print()
        lang_table = Table(title="Chunks by Language", show_header=True, header_style="bold magenta")
        lang_table.add_column("Language", style="cyan", no_wrap=True)
        lang_table.add_column("Count", style="green", justify="right")
        lang_table.add_column("Percentage", style="yellow", justify="right")
        
        total = stats['total_chunks']
        for language, count in sorted(stats['chunks_by_language'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            lang_table.add_row(language, str(count), f"{percentage:.1f}%")
        
        console.print(lang_table)
    
    return 0


def cmd_clear(args):
    """Clear the database"""
    print_warning("This will delete all indexed data!")
    
    if not args.yes:
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print_info("Operation cancelled")
            return 0
    
    # Initialize RAG system and clear
    rag = ChromeRAGSystem(db_path=args.db_path)
    rag.clear_collection()
    
    # Clear incremental state
    from utils.state_manager import StateManager
    StateManager().clear()
    
    print_success("Database cleared successfully")
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Chrome Source Code RAG System - Professional code indexing and search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index Chrome source code
  %(prog)s index --path /path/to/chromium/src
  
  # Index only C++ files
  %(prog)s index --path /path/to/chromium/src --file-types cpp
  
  # Search for code
  %(prog)s search --query "buffer overflow vulnerability"
  
  # Find a specific symbol
  %(prog)s symbol --name RenderFrameHost --type class
  
  # View statistics
  %(prog)s stats
        """
    )
    
    parser.add_argument(
        '--db-path',
        default=CONFIG.db_path,
        help=f'Path to ChromaDB database (default: {CONFIG.db_path})'
    )
    
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Index Chrome source directory')
    index_parser.add_argument('--path', required=True, help='Path to Chrome src/ directory')
    index_parser.add_argument('--file-types', help='Comma-separated list of file types (cpp,python,javascript,mojom,gn)')
    index_parser.add_argument('--batch-size', type=int, default=CONFIG.batch_size, help=f'Batch size for database operations (default: {CONFIG.batch_size})')
    index_parser.add_argument('--clear', action='store_true', help='Clear existing database before indexing')
    index_parser.add_argument('--force', action='store_true', help='Force re-indexing of all files (ignore incremental state)')
    index_parser.add_argument('--no-parallel', action='store_true', help='Disable parallel processing (use single thread)')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Semantic search for code')
    search_parser.add_argument('--query', required=True, help='Search query')
    search_parser.add_argument('--n-results', type=int, default=5, help='Number of results (default: 5)')
    search_parser.add_argument('--language', help='Filter by language (cpp, python, javascript, mojom, gn)')
    search_parser.add_argument('--type', help='Filter by type (function, class, method, etc.)')
    search_parser.add_argument('--full', action='store_true', help='Show full code without truncation')
    
    # Symbol command
    symbol_parser = subparsers.add_parser('symbol', help='Lookup specific symbol by name')
    symbol_parser.add_argument('--name', required=True, help='Symbol name')
    symbol_parser.add_argument('--type', help='Symbol type (function, class, method, etc.)')
    symbol_parser.add_argument('--language', help='Language filter (cpp, python, javascript, mojom, gn)')
    symbol_parser.add_argument('--n-results', type=int, default=5, help='Maximum results (default: 5)')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Display database statistics')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear the database')
    clear_parser.add_argument('--yes', action='store_true', help='Skip confirmation prompt')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging
    setup_logger(level=args.log_level)
    
    # Execute command
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        'index': cmd_index,
        'search': cmd_search,
        'symbol': cmd_symbol,
        'stats': cmd_stats,
        'clear': cmd_clear
    }
    
    try:
        return commands[args.command](args)
    except KeyboardInterrupt:
        print_warning("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
