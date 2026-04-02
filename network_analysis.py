#!/usr/bin/env python3
"""
CS Knowledge Graph Network Completeness Analyzer
Analyzes the markdown file structure, connections, and identifies issues.
"""

import os
import re
from collections import defaultdict, Counter
from pathlib import Path

# Configuration
BASE_DIR = "/mnt/d/Code/CS-Knowledge-Graph"

# Define the 6 main domains
DOMAINS = [
    "computer-science",
    "ai-data-systems", 
    "cloud-devops",
    "security",
    "software-engineering",
    "product-management",
    "mathematics"
]

def get_all_md_files():
    """Get all markdown files recursively."""
    md_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        # Skip hidden directories and .git
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            if f.endswith('.md'):
                full_path = os.path.join(root, f)
                # Normalize path
                rel_path = os.path.relpath(full_path, BASE_DIR)
                md_files.append(rel_path)
    return sorted(md_files)

def has_related_concepts_section(content):
    """Check if file has '相关概念' section."""
    return '相关概念' in content or '## 相关概念' in content

def extract_links(content, file_path):
    """Extract all markdown internal links from content."""
    # Pattern to match [text](path.md) or [text](../path/file.md) etc.
    pattern = r'\[([^\]]+)\]\(([^)]+\.md[^)]*)\)'
    matches = re.findall(pattern, content)
    
    links = []
    for text, link_path in matches:
        # Clean up the link path
        link_path = link_path.split('#')[0]  # Remove anchors
        link_path = link_path.strip()
        
        # Resolve relative paths
        if link_path.startswith('./'):
            # Relative to current directory
            current_dir = os.path.dirname(file_path)
            resolved = os.path.normpath(os.path.join(current_dir, link_path[2:]))
        elif link_path.startswith('../'):
            # Relative parent path
            current_dir = os.path.dirname(file_path)
            resolved = os.path.normpath(os.path.join(current_dir, link_path))
        elif not link_path.startswith('/'):
            # Could be relative or absolute within repo
            if '/' in link_path:
                # Contains path separators - treat as relative to base
                resolved = link_path
            else:
                # Just a filename - same directory
                current_dir = os.path.dirname(file_path)
                resolved = os.path.join(current_dir, link_path) if current_dir else link_path
        else:
            resolved = link_path.lstrip('/')
        
        links.append({
            'text': text,
            'raw_path': link_path,
            'resolved_path': resolved.replace('\\', '/'),
            'source_file': file_path
        })
    
    return links

def get_domain_from_path(file_path):
    """Extract domain from file path."""
    parts = file_path.split('/')
    if len(parts) > 0:
        first_part = parts[0]
        if first_part in DOMAINS:
            return first_part
    return None

def analyze_network():
    """Main analysis function."""
    print("=" * 80)
    print("CS KNOWLEDGE GRAPH NETWORK COMPLETENESS ANALYSIS")
    print("=" * 80)
    
    # Get all markdown files
    md_files = get_all_md_files()
    print(f"\n📊 TOTAL MARKDOWN FILES: {len(md_files)}")
    
    # Analysis containers
    files_with_related = []
    files_without_related = []
    all_links = []
    file_to_links = defaultdict(list)  # file -> links it contains (outgoing)
    link_targets = defaultdict(list)   # target -> files linking to it (incoming)
    domain_stats = defaultdict(lambda: {'count': 0, 'links_out': 0, 'links_in': 0, 'external_links': 0})
    
    # Process each file
    for file_path in md_files:
        full_path = os.path.join(BASE_DIR, file_path)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"  ⚠️ Error reading {file_path}: {e}")
            continue
        
        # Check for related concepts section
        if has_related_concepts_section(content):
            files_with_related.append(file_path)
        else:
            files_without_related.append(file_path)
        
        # Extract links
        links = extract_links(content, file_path)
        file_to_links[file_path] = links
        all_links.extend(links)
        
        # Track incoming links
        for link in links:
            link_targets[link['resolved_path']].append({
                'source': file_path,
                'text': link['text'],
                'raw_path': link['raw_path']
            })
        
        # Domain stats
        domain = get_domain_from_path(file_path)
        if domain:
            domain_stats[domain]['count'] += 1
    
    # Print related concepts statistics
    print(f"\n📋 FILES WITH '相关概念' SECTION:")
    print(f"   ✓ With section:    {len(files_with_related)} ({len(files_with_related)/len(md_files)*100:.1f}%)")
    print(f"   ✗ Without section: {len(files_without_related)} ({len(files_without_related)/len(md_files)*100:.1f}%)")
    
    # Check which files are missing the section
    if files_without_related:
        print(f"\n   Files missing '相关概念' section:")
        for f in sorted(files_without_related)[:20]:  # Show first 20
            print(f"      - {f}")
        if len(files_without_related) > 20:
            print(f"      ... and {len(files_without_related) - 20} more")
    
    # Link statistics
    print(f"\n🔗 LINK ANALYSIS:")
    print(f"   Total links found: {len(all_links)}")
    print(f"   Unique link targets: {len(set(l['resolved_path'] for l in all_links))}")
    
    # Find orphaned files (no incoming and no outgoing links)
    print(f"\n🚨 ORPHANED FILES (no incoming or outgoing internal links):")
    orphaned = []
    for file_path in md_files:
        outgoing = len(file_to_links.get(file_path, []))
        incoming = len(link_targets.get(file_path, []))
        if outgoing == 0 and incoming == 0:
            orphaned.append(file_path)
    
    if orphaned:
        for f in orphaned:
            print(f"   - {f}")
    else:
        print("   None found! ✓")
    
    # Find files with no outgoing links (but may have incoming)
    print(f"\n📤 FILES WITH NO OUTGOING LINKS (dead ends):")
    dead_ends = []
    for file_path in md_files:
        outgoing = len(file_to_links.get(file_path, []))
        if outgoing == 0:
            incoming = len(link_targets.get(file_path, []))
            dead_ends.append((file_path, incoming))
    
    dead_ends.sort(key=lambda x: -x[1])  # Sort by incoming links desc
    for f, incoming in dead_ends[:15]:
        print(f"   - {f} (incoming: {incoming})")
    if len(dead_ends) > 15:
        print(f"   ... and {len(dead_ends) - 15} more")
    
    # Find files with no incoming links (unreachable)
    print(f"\n📥 FILES WITH NO INCOMING LINKS (potentially unreachable):")
    unreachable = []
    for file_path in md_files:
        incoming = len(link_targets.get(file_path, []))
        if incoming == 0:
            outgoing = len(file_to_links.get(file_path, []))
            unreachable.append((file_path, outgoing))
    
    unreachable.sort(key=lambda x: -x[1])  # Sort by outgoing links desc
    for f, outgoing in unreachable[:15]:
        print(f"   - {f} (outgoing: {outgoing})")
    if len(unreachable) > 15:
        print(f"   ... and {len(unreachable) - 15} more")
    
    # Check for broken links
    print(f"\n💔 BROKEN LINKS (target file does not exist):")
    broken = []
    for link in all_links:
        target = link['resolved_path']
        # Check if target exists
        if target not in md_files:
            # Try with different variations
            found = False
            for md_file in md_files:
                if md_file.endswith(target) or target.endswith(md_file):
                    found = True
                    break
            if not found:
                broken.append({
                    'source': link['source_file'],
                    'target': target,
                    'text': link['text']
                })
    
    if broken:
        # Group by source
        by_source = defaultdict(list)
        for b in broken:
            by_source[b['source']].append(b)
        
        for source, links in sorted(by_source.items())[:10]:
            print(f"   In {source}:")
            for b in links[:5]:
                print(f"      → '{b['text']}' → {b['target']}")
            if len(links) > 5:
                print(f"      ... and {len(links) - 5} more")
    else:
        print("   None found! ✓")
    
    # Domain connectivity analysis
    print(f"\n🌐 DOMAIN CONNECTIVITY ANALYSIS:")
    print(f"\n   Domain file counts:")
    for domain in DOMAINS:
        count = domain_stats[domain]['count']
        print(f"      {domain}: {count} files")
    
    # Build domain link matrix
    domain_links = defaultdict(lambda: defaultdict(int))
    for link in all_links:
        source_domain = get_domain_from_path(link['source_file'])
        target_domain = get_domain_from_path(link['resolved_path'])
        if source_domain and target_domain:
            domain_links[source_domain][target_domain] += 1
    
    print(f"\n   Domain-to-Domain Link Matrix:")
    print(f"   {'From/To':<25}", end='')
    for d in DOMAINS:
        print(f"{d[:12]:<12}", end='')
    print()
    print(f"   {'-'*25}", end='')
    for _ in DOMAINS:
        print(f"{'-'*12}", end='')
    print()
    
    for source in DOMAINS:
        print(f"   {source:<25}", end='')
        for target in DOMAINS:
            count = domain_links[source][target]
            if source == target:
                print(f"{'['+str(count)+']':<12}", end='')  # Internal links in brackets
            elif count > 0:
                print(f"{count:<12}", end='')
            else:
                print(f"{'-':<12}", end='')
        print()
    
    # Check for isolated domain pairs
    print(f"\n   🔍 Domain Connection Gaps (no direct links):")
    gaps_found = False
    for d1 in DOMAINS:
        for d2 in DOMAINS:
            if d1 != d2:
                if domain_links[d1][d2] == 0 and domain_links[d2][d1] == 0:
                    print(f"      {d1} ↔ {d2}")
                    gaps_found = True
    if not gaps_found:
        print("      None - all domains are connected! ✓")
    
    # Find cross-domain connections
    print(f"\n   Cross-domain link counts:")
    for source in DOMAINS:
        internal = domain_links[source][source]
        external = sum(domain_links[source][t] for t in DOMAINS if t != source)
        print(f"      {source}: {internal} internal, {external} external")
    
    # Most connected files
    print(f"\n⭐ MOST CONNECTED FILES (by total link count):")
    file_scores = []
    for file_path in md_files:
        incoming = len(link_targets.get(file_path, []))
        outgoing = len(file_to_links.get(file_path, []))
        file_scores.append((file_path, incoming, outgoing, incoming + outgoing))
    
    file_scores.sort(key=lambda x: -x[3])
    print(f"   {'File':<60} {'In':>5} {'Out':>5} {'Total':>5}")
    print(f"   {'-'*60} {'-'*5} {'-'*5} {'-'*5}")
    for f, inc, out, total in file_scores[:15]:
        print(f"   {f:<60} {inc:>5} {out:>5} {total:>5}")
    
    # Structural issues
    print(f"\n⚠️ STRUCTURAL ISSUES DETECTED:")
    
    # Check for empty files
    print(f"\n   Empty or nearly empty files:")
    empty_files = []
    for file_path in md_files:
        full_path = os.path.join(BASE_DIR, file_path)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if len(content) < 100:
                    empty_files.append((file_path, len(content)))
        except:
            pass
    
    if empty_files:
        for f, size in sorted(empty_files, key=lambda x: x[1]):
            print(f"      - {f} ({size} chars)")
    else:
        print("   None found ✓")
    
    # Check for files with no headers
    print(f"\n   Files missing proper markdown headers (#):")
    no_headers = []
    for file_path in md_files:
        full_path = os.path.join(BASE_DIR, file_path)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not re.search(r'^#+ ', content, re.MULTILINE):
                    no_headers.append(file_path)
        except:
            pass
    
    if no_headers:
        for f in no_headers[:10]:
            print(f"      - {f}")
        if len(no_headers) > 10:
            print(f"      ... and {len(no_headers) - 10} more")
    else:
        print("   None found ✓")
    
    # Summary
    print(f"\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"""
📈 STATISTICS:
   • Total markdown files: {len(md_files)}
   • Files with '相关概念' section: {len(files_with_related)} ({len(files_with_related)/len(md_files)*100:.1f}%)
   • Total internal links: {len(all_links)}
   • Orphaned files (no connections): {len(orphaned)}
   • Dead-end files (no outgoing): {len(dead_ends)}
   • Potentially unreachable (no incoming): {len(unreachable)}
   • Broken links: {len(broken)}

🎯 RECOMMENDATIONS:
   1. Add '相关概念' section to {len(files_without_related)} files ({len(files_without_related)/len(md_files)*100:.1f}%)
   2. Connect orphaned files to the knowledge graph
   3. Fix broken links: {len(broken)}
   4. Consider linking dead-end files to related concepts
""")

if __name__ == "__main__":
    analyze_network()
