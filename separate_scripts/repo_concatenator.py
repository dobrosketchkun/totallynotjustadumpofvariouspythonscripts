#!/usr/bin/env python3
"""
Repository Concatenator

This script concatenates all files from a directory into a single file,
with configurable filtering options and directory structure display.
Configuration is provided via a YAML file.
"""

import os
import sys
import argparse
import fnmatch
import re
import json
import yaml
from pathlib import Path


def generate_tree(directory, prefix="", config=None, show_root=True):
    """
    Generate a visual tree representation of the directory structure
    with the same filtering rules applied to the concatenation process.
    
    Args:
        directory (str): Directory to process
        prefix (str): Prefix for tree display
        config (dict): Configuration dictionary
        show_root (bool): Whether to show the root directory name
    """
    if config is None:
        config = {}
    
    exclude_patterns = config.get('exclude_patterns', [])
    include_patterns = config.get('include_patterns', [])
    exclude_dirs = config.get('exclude_dirs', [])
    exclude_exts = config.get('exclude_exts', [])
    include_exts = config.get('include_exts', [])
    whitelist = config.get('whitelist', [])
    blacklist = config.get('blacklist', [])
    
    output = []
    
    # Add root directory name if requested and we're at the beginning
    if show_root and prefix == "":
        root_name = os.path.basename(os.path.abspath(directory))
        output.append(root_name)
        prefix = "  "
    
    # Get and sort directory contents
    try:
        contents = sorted(os.listdir(directory))
    except PermissionError:
        return [f"{prefix}├── {os.path.basename(directory)} [Permission Denied]"]
    except Exception as e:
        return [f"{prefix}├── {os.path.basename(directory)} [Error: {str(e)}]"]
    
    # Apply filtering rules to the directory listing
    filtered_contents = []
    for item in contents:
        item_path = os.path.join(directory, item)
        
        # Skip items in blacklist
        if blacklist and item in blacklist:
            continue
        
        # Only include items in whitelist if it's specified
        if whitelist and item not in whitelist:
            continue
        
        # Skip directories matching excluded patterns
        if exclude_dirs and os.path.isdir(item_path):
            if any(fnmatch.fnmatch(item, pattern) for pattern in exclude_dirs):
                continue
        
        # Skip files with excluded extensions
        if exclude_exts and os.path.isfile(item_path):
            ext = os.path.splitext(item)[1].lstrip('.')
            if ext in exclude_exts:
                continue
        
        # Only include files with specific extensions if include_exts is specified
        if include_exts and os.path.isfile(item_path):
            ext = os.path.splitext(item)[1].lstrip('.')
            if ext not in include_exts:
                continue
        
        # Skip files/dirs matching excluded patterns
        if exclude_patterns and any(re.search(pattern, item_path) for pattern in exclude_patterns):
            continue
        
        # Only include files/dirs matching include patterns if specified
        if include_patterns and not any(re.search(pattern, item_path) for pattern in include_patterns):
            continue
        
        filtered_contents.append(item)
    
    # Process each item in the directory
    for i, item in enumerate(filtered_contents):
        item_path = os.path.join(directory, item)
        is_last = i == len(filtered_contents) - 1
        
        # Choose the appropriate prefix characters
        current_prefix = prefix + ("└── " if is_last else "├── ")
        next_prefix = prefix + ("    " if is_last else "│   ")
        
        # Add the current item to the output
        output.append(f"{current_prefix}{item}")
        
        # Recursively process subdirectories
        if os.path.isdir(item_path):
            output.extend(generate_tree(item_path, next_prefix, config, False))
    
    return output


def concatenate_files(directory, output_file, config=None):
    """
    Concatenate all files in the directory and its subdirectories into one file
    with filtering capabilities.
    
    Args:
        directory (str): Source directory
        output_file (str): Destination file
        config (dict): Configuration dictionary
    """
    if config is None:
        config = {}
    
    delimiter = config.get('delimiter', "\n----------\n")
    exclude_patterns = config.get('exclude_patterns', [])
    include_patterns = config.get('include_patterns', [])
    exclude_dirs = config.get('exclude_dirs', [])
    exclude_exts = config.get('exclude_exts', [])
    include_exts = config.get('include_exts', [])
    whitelist = config.get('whitelist', [])
    blacklist = config.get('blacklist', [])
    max_file_size = config.get('max_file_size', -1)
    
    with open(output_file, 'w', encoding='utf-8', errors='replace') as outfile:
        # Generate and write the directory tree
        outfile.write("Directory Tree:\n")
        tree = generate_tree(directory, prefix="", config=config, show_root=True)
        outfile.write("\n".join(tree))
        outfile.write("\n\n" + "="*80 + "\n\n")
        
        # Walk through the directory
        for root, dirs, files in os.walk(directory):
            # Apply directory exclusion patterns
            if exclude_dirs:
                dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, pattern) for pattern in exclude_dirs)]
            
            # Apply path patterns for directories
            if exclude_patterns:
                dirs[:] = [d for d in dirs if not any(re.search(pattern, os.path.join(root, d)) for pattern in exclude_patterns)]
            
            if include_patterns:
                dirs[:] = [d for d in dirs if any(re.search(pattern, os.path.join(root, d)) for pattern in include_patterns)]
            
            # Sort files for consistent output
            files.sort()
            
            # Process each file
            for filename in files:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, directory)
                
                # Skip files in blacklist
                if blacklist and filename in blacklist:
                    continue
                
                # Only include files in whitelist if it's specified
                if whitelist and filename not in whitelist:
                    continue
                
                # Skip files with excluded extensions
                if exclude_exts:
                    ext = os.path.splitext(filename)[1].lstrip('.')
                    if ext in exclude_exts:
                        continue
                
                # Only include files with specific extensions if include_exts is specified
                if include_exts:
                    ext = os.path.splitext(filename)[1].lstrip('.')
                    if ext not in include_exts:
                        continue
                
                # Skip files matching excluded patterns
                if exclude_patterns and any(re.search(pattern, file_path) for pattern in exclude_patterns):
                    continue
                
                # Only include files matching include patterns if specified
                if include_patterns and not any(re.search(pattern, file_path) for pattern in include_patterns):
                    continue
                
                # Check file size
                if max_file_size and max_file_size > 0:  # Allow -1 to mean "no limit"
                    try:
                        if os.path.getsize(file_path) > max_file_size:
                            outfile.write(f"\n{delimiter}\n### FILE: {rel_path} [SKIPPED - EXCEEDS SIZE LIMIT]\n{delimiter}\n")
                            continue
                    except (OSError, IOError) as e:
                        outfile.write(f"\n{delimiter}\n### FILE: {rel_path} [ERROR: {str(e)}]\n{delimiter}\n")
                        continue
                
                # Try to read and write the file content
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as infile:
                        outfile.write(f"\n{delimiter}\n### FILE: {rel_path}\n{delimiter}\n")
                        outfile.write(infile.read())
                except (UnicodeDecodeError, OSError, IOError) as e:
                    outfile.write(f"\n{delimiter}\n### FILE: {rel_path} [ERROR: {str(e)}]\n{delimiter}\n")


def load_config(config_file):
    """
    Load configuration from a YAML or JSON file.
    """
    try:
        with open(config_file, 'r') as f:
            if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                config = yaml.safe_load(f)
            else:
                # Try YAML first even for non-yaml extensions
                try:
                    config = yaml.safe_load(f)
                except yaml.YAMLError:
                    # Fall back to JSON if YAML parsing fails
                    f.seek(0)  # Reset file pointer to beginning
                    config = json.load(f)
        return config
    except Exception as e:
        print(f"Error loading config file: {str(e)}", file=sys.stderr)
        sys.exit(1)


def create_sample_config():
    """
    Create a detailed sample configuration file in YAML format.
    """
    # Create a temporary file with comments that will be preserved in the output
    sample_config = """# Repository Concatenator Configuration
# =================================
# This configuration file controls how the repository concatenator processes files.
# All filtering options can be combined to precisely control which files are included.

# Basic Settings
# -------------
# Required settings for input and output
source: "/path/to/source/directory"   # Directory to process (required)
output: "output.txt"                  # Output file path (required)
delimiter: "\\n----------\\n"           # Text separator between files

# Regular Expression Pattern Filtering
# -----------------------------------
# Uses Python regex patterns to include or exclude files and directories
# Note: Backslashes must be escaped with another backslash in YAML

exclude_patterns:
  - "test_.*\\\\.py"      # Exclude test files
  - "\\\\.git/.*"         # Exclude git internals
  - ".*\\\\.tmp$"         # Exclude temporary files
  - "build/.*\\\\.log"    # Exclude log files in build directory

include_patterns: []    # Empty means include everything not excluded
# include_patterns:     # When specified, ONLY include files matching these patterns
#   - "src/.*\\\\.py"     # Only include Python files in the src directory
#   - "docs/.*\\\\.md"    # Only include Markdown files in the docs directory

# Directory Filtering
# -----------------
# Uses glob-style patterns (fnmatch) to filter directories
# Directories matching any of these patterns will be completely skipped

exclude_dirs:
  - ".*"                # Exclude hidden directories (starting with .)
  - "node_modules"      # Exclude node dependencies
  - "__pycache__"       # Exclude Python cache
  - "venv"              # Exclude virtual environments
  - ".venv"             # Exclude another common virtual env name
  - "env"               # Exclude another common virtual env name
  - "build"             # Exclude build directories
  - "dist"              # Exclude distribution directories
  - "target"            # Exclude target directories (common in Java, Rust)
  - ".git"              # Exclude git directory
  - ".svn"              # Exclude svn directory
  - ".hg"               # Exclude mercurial directory
  - ".idea"             # Exclude JetBrains IDE settings
  - ".vscode"           # Exclude VS Code settings

# File Extension Filtering
# ----------------------
# Filter files based on their extension (without the dot)

exclude_exts:
  # Binary and executable files
  - "exe"               # Windows executables
  - "dll"               # Dynamic link libraries
  - "so"                # Shared objects (Linux)
  - "dylib"             # Dynamic libraries (macOS)
  - "bin"               # Generic binary files
  
  # Compiled code
  - "pyc"               # Python bytecode
  - "pyo"               # Optimized Python bytecode
  - "pyd"               # Python DLLs
  - "class"             # Java bytecode
  - "o"                 # Object files
  - "obj"               # Object files
  - "a"                 # Static libraries
  - "lib"               # Library files
  
  # Media files
  - "jpg"               # JPEG images
  - "jpeg"              # JPEG images
  - "png"               # PNG images
  - "gif"               # GIF images
  - "bmp"               # Bitmap images
  - "svg"               # Scalable Vector Graphics
  - "ico"               # Icon files
  - "mp3"               # MP3 audio
  - "wav"               # WAV audio
  - "mp4"               # MP4 video
  - "avi"               # AVI video
  - "mov"               # QuickTime video
  
  # Archive files
  - "zip"               # ZIP archives
  - "tar"               # TAR archives
  - "gz"                # Gzipped files
  - "rar"               # RAR archives
  - "7z"                # 7-Zip archives
  
  # Database files
  - "db"                # Generic database files
  - "sqlite"            # SQLite database
  - "sqlite3"           # SQLite3 database

# Alternatively, specify which extensions to include (overrides exclude_exts)
include_exts: []        # Empty means include all extensions not excluded
# include_exts:         # When specified, ONLY include these extensions
#   - "py"              # Python files
#   - "js"              # JavaScript files
#   - "ts"              # TypeScript files
#   - "jsx"             # React JSX files
#   - "tsx"             # React TSX files
#   - "md"              # Markdown files
#   - "rst"             # reStructuredText files
#   - "txt"             # Text files
#   - "yml"             # YAML files
#   - "yaml"            # YAML files
#   - "json"            # JSON files
#   - "toml"            # TOML files
#   - "ini"             # INI configuration files
#   - "cfg"             # Configuration files
#   - "conf"            # Configuration files
#   - "xml"             # XML files
#   - "html"            # HTML files
#   - "css"             # CSS files
#   - "scss"            # SCSS files
#   - "sass"            # Sass files
#   - "less"            # Less files

# Specific File Filtering
# ---------------------
# Explicitly control individual files by name

whitelist: []           # Empty means include all files not otherwise excluded
# whitelist:            # When not empty, ONLY include these specific files
#   - "main.py"         # Include main.py
#   - "README.md"       # Include README.md
#   - "setup.py"        # Include setup.py
#   - "requirements.txt" # Include requirements.txt

blacklist:              # Always exclude these specific files
  - ".gitignore"        # Git ignore file
  - ".gitattributes"    # Git attributes file
  - ".gitmodules"       # Git submodules file
  - ".gitkeep"          # Git file for empty folders
  - ".dockerignore"     # Docker ignore file
  - "Dockerfile"        # Docker file
  - ".editorconfig"     # Editor config file
  - ".prettierrc"       # Prettier config file
  - ".eslintrc"         # ESLint config file
  - "package-lock.json" # NPM lock file
  - "yarn.lock"         # Yarn lock file
  - "Pipfile.lock"      # Pipenv lock file
  - "poetry.lock"       # Poetry lock file
  - ".DS_Store"         # macOS directory metadata
  - "Thumbs.db"         # Windows thumbnail cache
  - ".env"              # API keys and such

# Size Limits
# ----------
# Control handling of large files

# max_file_size: 1048576  # Skip files larger than 1MB (1024*1024 bytes)
max_file_size: -1     # Use -1 for no size limit - include all files regardless of size
"""
    
    # Write YAML sample
    with open('repo_concatenator_config_sample.yaml', 'w') as f:
        f.write(sample_config)
    
    print("Created sample configuration file:")
    print("  - repo_concatenator_config_sample.yaml")


def main():
    parser = argparse.ArgumentParser(description="Concatenate all files in a directory into one file using a configuration file.")
    
    # Only two options: config file path or create sample config
    parser.add_argument("config", nargs="?", help="Path to configuration file (YAML)")
    parser.add_argument("--create-sample-config", action="store_true", help="Create sample configuration file and exit")
    
    args = parser.parse_args()
    
    # Create sample config if requested
    if args.create_sample_config:
        create_sample_config()
        return 0
    
    # Load configuration from file
    if not args.config:
        parser.print_help()
        print("\nError: You must specify a configuration file or use --create-sample-config", file=sys.stderr)
        return 1
    
    config = load_config(args.config)
    
    # Validate required parameters
    source = config.get('source')
    output = config.get('output')
    
    if not source or not output:
        print(f"Error: 'source' and 'output' must be specified in config file", file=sys.stderr)
        return 1
    
    if not os.path.isdir(source):
        print(f"Error: Source directory '{source}' does not exist or is not a directory.", file=sys.stderr)
        return 1
    
    try:
        concatenate_files(source, output, config)
        print(f"Successfully concatenated files from '{source}' to '{output}'")
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
