#!/usr/bin/env python3
import os
import argparse
from pathlib import Path

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def format_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(0)
    p = float(size_bytes)
    while p >= 1024 and i < len(size_name) - 1:
        p /= 1024
        i += 1
    return f"{p:.2f} {size_name[i]}"

def analyze_repo(repo_path):
    repo_path = Path(repo_path).resolve()
    print(f"Analyzing: {repo_path}")
    
    stats = {
        'git': 0,
        'third_party': 0,
        'build': 0,
        'source_code': 0,
        'assets_other': 0
    }
    
    # Extensions we consider "Source Code"
    source_exts = {
        '.c', '.cc', '.cpp', '.cxx', '.h', '.hpp', 
        '.py', '.java', '.js', '.ts', '.go', '.rs', 
        '.rb', '.php', '.cs', '.gn', '.gni', '.mojom'
    }
    
    # Specific directories to track
    special_dirs = {
        '.git': 'git',
        'third_party': 'third_party',
        'out': 'build',
        'build': 'build'
    }

    for root, dirs, files in os.walk(repo_path):
        root_path = Path(root)
        
        # Determine category based on path
        category = 'other'
        
        # Check if we are inside a special directory
        rel_path = root_path.relative_to(repo_path)
        parts = rel_path.parts
        
        if len(parts) > 0:
            top_dir = parts[0]
            if top_dir in special_dirs:
                category = special_dirs[top_dir]
        
        for f in files:
            fp = root_path / f
            if fp.is_symlink():
                continue
                
            try:
                size = fp.stat().st_size
                
                if category != 'other':
                    stats[category] += size
                else:
                    # Check if it's source code or asset
                    if fp.suffix in source_exts:
                        stats['source_code'] += size
                    else:
                        stats['assets_other'] += size
                        
            except Exception:
                pass

    print("\n--- Repository Breakdown ---")
    print(f"📂 .git folder:      {format_size(stats['git'])}")
    print(f"📦 third_party:      {format_size(stats['third_party'])}")
    print(f"🏗️  out/build:        {format_size(stats['build'])}")
    print(f"📝 Source Code:      {format_size(stats['source_code'])} (Actual Indexable Code)")
    print(f"🖼️  Assets/Other:     {format_size(stats['assets_other'])}")
    
    total = sum(stats.values())
    print(f"\nTotal Size: {format_size(total)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze repository size breakdown")
    parser.add_argument("--path", default=".", help="Path to repository")
    args = parser.parse_args()
    
    analyze_repo(args.path)
