#!/usr/bin/env python3
"""
Professional logging system with colored output and progress tracking
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn


# Global console for rich output
console = Console()


def setup_logger(name: str = "chrome_rag", log_file: Optional[str] = None, level: str = "INFO") -> logging.Logger:
    """
    Setup a logger with rich console output and optional file logging
    
    Args:
        name: Logger name
        log_file: Optional file path for logging
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Rich console handler
    console_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        markup=True,
        rich_tracebacks=True
    )
    console_handler.setLevel(getattr(logging, level.upper()))
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "chrome_rag") -> logging.Logger:
    """Get existing logger or create a new one"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger


def create_progress_bar() -> Progress:
    """Create a rich progress bar for tracking long operations"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console
    )


def print_success(message: str):
    """Print a success message"""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str):
    """Print an error message"""
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str):
    """Print a warning message"""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_info(message: str):
    """Print an info message"""
    console.print(f"[blue]ℹ[/blue] {message}")


def print_header(message: str):
    """Print a header message"""
    console.print(f"\n[bold cyan]{message}[/bold cyan]")
    console.print("[cyan]" + "=" * len(message) + "[/cyan]\n")


def print_stats(stats: dict):
    """Print statistics in a formatted table"""
    from rich.table import Table
    
    table = Table(title="Indexing Statistics", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    
    for key, value in stats.items():
        table.add_row(key, str(value))
    
    console.print(table)
