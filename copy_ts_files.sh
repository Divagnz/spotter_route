#!/bin/bash

# Set source and destination directories
SRC_DIR="."
DEST_DIR="/home/diva/testing"

# Create destination directory if it doesn't exist
mkdir -p "$DEST_DIR"

# Find all .ts and .tsx files
find "$SRC_DIR" -type d \( -name ".next" -o -name "node_modules" \) -prune -o -type f \( -name "*.py" -o -name "*.tsx" \) -print | while read -r file; do
    # Get relative path
    rel_path=$(dirname "${file#./}")
    
    # Get filename
    filename=$(basename "$file")
    
    # Get extension
    ext="${filename##*.}"
    
    # Get filename without extension
    name="${filename%.*}"
    
    if [[ "$name" == "index" ]]; then
        new_name="${rel_path}"
        # Remove trailing slash if present
        new_name="${new_name%|}"
    else
        new_name="${rel_path}|${name}"
    fi
    
    # Remove leading slash if present
    new_name="${new_name#|}"
    new_name="${new_name//\//|}"
    # Copy the file with the new name
    cp "$file" $DEST_DIR/"${new_name}.${ext}"
    
    echo "Copied: $file -> $DEST_DIR/${new_name}.${ext}"
done
