#!/bin/bash
# Script to remove hex prefixes from all markdown files
# Usage: ./fix_hex_prefixes.sh

find /mnt/d/Code/CS-Knowledge-Graph -name "*.md" -type f | while read -r file; do
    # Remove hex prefixes like #ABC| from the beginning of lines
    # Pattern: #[A-Z]{2,3}| at the start of a line
    sed -i 's/^[0-9]*#[A-Z]\{2,3\}|//g' "$file"
done

echo "Hex prefix removal complete!"