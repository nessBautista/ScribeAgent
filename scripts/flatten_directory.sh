#!/bin/bash

# Show usage instructions if -h or --help flag is used
show_help() {
    cat << EOF
Swift Files Directory Flattening Script
-------------------------------------
This script creates a flattened copy of a directory structure, where all Swift,
Markdown, PDF, Python, and TOML files from the main project directory are placed in a single directory
with their paths encoded in their filenames.

Usage:
    ./flatten_directory.sh [options]
    
Options:
    -h, --help      Show this help message
    -p, --path      Specify the path to flatten (default: current directory)
    -o, --output    Specify the output directory (default: input_path + "_flat")
    -d, --dry-run   Show what would be copied without making changes
    
Example:
    ./flatten_directory.sh                                    # Flatten current directory
    ./flatten_directory.sh -p /path/to/dir                   # Flatten specific directory
    ./flatten_directory.sh -p /path/to/dir -o /output/dir    # Specify output directory

The script will:
1. Create a new directory with "_flat" suffix
2. Copy relevant files (.swift, .md, .pdf, and .py) to this new directory
3. Rename files to include their original path (using underscores)
4. Ignore the .build directory and other non-relevant paths
5. Preserve the original directory structure

Note: The original directory structure remains unchanged.
Only .swift, .md, .pdf, .py, and .toml files from the main project directory will be processed.
EOF
    exit 0
}

# Parse command line arguments
DIRECTORY="$(pwd)"
OUTPUT_DIR=""
DRY_RUN=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        -p|--path)
            DIRECTORY="$2"
            shift
            shift
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

# Validate the directory
if [ ! -d "$DIRECTORY" ]; then
    echo "Error: Directory '$DIRECTORY' does not exist!"
    exit 1
fi

# Convert to absolute path
DIRECTORY=$(cd "$DIRECTORY"; pwd)

# Get the directory where the script is run
current_dir="$DIRECTORY"

# Set default output directory if not specified
if [ -z "$OUTPUT_DIR" ]; then
    OUTPUT_DIR="${DIRECTORY}_flat"
fi

# Create a new directory for the flattened structure
flat_dir="$OUTPUT_DIR"
echo "Creating flattened directory at: $flat_dir"

# Create the output directory (only if not dry run)
if [ "$DRY_RUN" = false ]; then
    mkdir -p "$flat_dir"
fi

# Function to process files recursively
process_directory() {
    local base_path="$1"
    local current_path="$2"
    
    # Loop through all files and directories in the current path
    find "$current_path" -mindepth 1 -maxdepth 1 \
        ! -path "*/\.*" \
        ! -path "*/\.build/*" \
        ! -path "*/\.build" \
        ! -path "*/DerivedData/*" \
        ! -path "*/Pods/*" \
        ! -path "*/vendor/*" \
        | while read -r item; do
        # Get the relative path from the base directory
        local rel_path="${item#$base_path/}"
        
        if [ -f "$item" ] && { [[ "$item" == *.swift ]] || [[ "$item" == *.md ]] || [[ "$item" == *.pdf ]] || [[ "$item" == *.py ]] || [[ "$item" == *.toml ]]; }; then
            # For Swift, Markdown, PDF, Python, and TOML files, create new name based on path
            local new_name=$(echo "$rel_path" | sed 's/\//_/g')
            # Copy to flattened directory
            if [ "$DRY_RUN" = true ]; then
                echo "[DRY RUN] Would copy: ${rel_path} -> ${new_name}"
            else
                if cp "$item" "${flat_dir}/${new_name}"; then
                    echo "Copied file: ${rel_path} -> ${new_name}"
                else
                    echo "Error copying file: ${rel_path}"
                fi
            fi
        elif [ -d "$item" ]; then
            # For directories, process their contents recursively
            process_directory "$base_path" "$item"
        fi
    done
}

# Main execution
echo "Starting directory flattening for Swift, Markdown, PDF, and Python files..."
echo "Original directory: $current_dir"

# Process the current directory
process_directory "$current_dir" "$current_dir"

# Check if any relevant files were copied
file_count=$(find "$flat_dir" \( -name "*.swift" -o -name "*.md" -o -name "*.pdf" -o -name "*.py" -o -name "*.toml" \) | wc -l)
if [ "$file_count" -eq 0 ] && [ "$DRY_RUN" = false ]; then
    echo "No Swift, Markdown, PDF, Python, or TOML files found in the directory structure!"
    rm -r "$flat_dir"
else
    if [ "$DRY_RUN" = true ]; then
        echo "Dry run complete! Would have processed files as shown above."
    else
        echo "Flattening complete! ${file_count} files are available in: $flat_dir"
    fi
fi