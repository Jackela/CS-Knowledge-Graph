#!/bin/bash
# Check which topics from CURRICULUM.md actually have files

echo "=== Checking Missing Topics ==="

# Compilers (5 files - should exist)
echo -e "\n--- Compilers ---"
for topic in lexical-analysis parsing semantic-analysis code-generation optimization; do
    if [ -f "/mnt/d/Code/CS-Knowledge-Graph/computer-science/compilers/${topic}.md" ]; then
        echo "✓ ${topic}.md exists"
    else
        echo "✗ ${topic}.md MISSING"
    fi
done

# Architecture Patterns (5 files)
echo -e "\n--- Architecture Patterns ---"
for topic in monolithic layered-architecture clean-architecture hexagonal-architecture serverless; do
    if [ -f "/mnt/d/Code/CS-Knowledge-Graph/software-engineering/architecture-patterns/${topic}.md" ]; then
        echo "✓ ${topic}.md exists"
    else
        echo "✗ ${topic}.md MISSING"
    fi
done

# Testing (5 files)
echo -e "\n--- Testing ---"
for topic in integration-testing e2e-testing bdd mocking performance-testing; do
    if [ -f "/mnt/d/Code/CS-Knowledge-Graph/software-engineering/testing/${topic}.md" ]; then
        echo "✓ ${topic}.md exists"
    else
        echo "✗ ${topic}.md MISSING"
    fi
done

# Calculus (6 files)
echo -e "\n--- Calculus ---"
for topic in limits-continuity derivatives integrals multivariable-calculus differential-equations; do
    if [ -f "/mnt/d/Code/CS-Knowledge-Graph/mathematics/calculus/${topic}.md" ]; then
        echo "✓ ${topic}.md exists"
    else
        echo "✗ ${topic}.md MISSING"
    fi
done

# DDD (10 files)
echo -e "\n--- Domain-Driven Design ---"
mkdir -p /mnt/d/Code/CS-Knowledge-Graph/software-engineering/ddd
for topic in domain-model bounded-context entities-value-objects aggregates repositories domain-services application-services domain-events anti-corruption-layer ubiquitous-language; do
    if [ -f "/mnt/d/Code/CS-Knowledge-Graph/software-engineering/ddd/${topic}.md" ]; then
        echo "✓ ${topic}.md exists"
    else
        echo "✗ ${topic}.md MISSING"
    fi
done

# Discrete Math (6 files)
echo -e "\n--- Discrete Mathematics ---"
mkdir -p /mnt/d/Code/CS-Knowledge-Graph/mathematics/discrete-mathematics
for topic in set-theory logic relations functions number-theory boolean-algebra; do
    if [ -f "/mnt/d/Code/CS-Knowledge-Graph/mathematics/discrete-mathematics/${topic}.md" ]; then
        echo "✓ ${topic}.md exists"
    else
        echo "✗ ${topic}.md MISSING"
    fi
done

# Graph Theory (6 files)
echo -e "\n--- Graph Theory ---"
mkdir -p /mnt/d/Code/CS-Knowledge-Graph/mathematics/graph-theory
for topic in graph-representations graph-traversal shortest-paths minimum-spanning-trees network-flow graph-algorithms; do
    if [ -f "/mnt/d/Code/CS-Knowledge-Graph/mathematics/graph-theory/${topic}.md" ]; then
        echo "✓ ${topic}.md exists"
    else
        echo "✗ ${topic}.md MISSING"
    fi
done

echo -e "\n=== Check Complete ==="