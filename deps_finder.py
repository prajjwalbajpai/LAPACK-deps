#!/usr/bin/env python3
import json
import sys

def load_graph(path):
    with open(path) as f:
        return json.load(f)

def collect_subgraph(start, graph):
    visited = set()
    edges = []

    def dfs(node):
        if node in visited:
            return
        visited.add(node)
        for child in graph.get(node, []):
            edges.append((node, child))
            dfs(child)

    dfs(start)
    return visited, edges

def write_dot(start, nodes, edges, filename):
    with open(filename, "w") as f:
        f.write("digraph G {\n")
        f.write("  rankdir=LR;\n")  # left to right layout
        f.write("  node [shape=box];\n\n")

        # Highlight root
        f.write(f'  "{start}" [style=filled, fillcolor=lightblue];\n\n')

        # Write edges
        for src, dst in edges:
            f.write(f'  "{src}" -> "{dst}";\n')

        f.write("}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python downward_to_dot.py output/graph.json dgesvd")
        sys.exit(1)

    path = sys.argv[1]
    start = sys.argv[2]

    graph = load_graph(path)

    if start not in graph:
        print(f"{start} not found in graph")
        sys.exit(1)

    nodes, edges = collect_subgraph(start, graph)

    output_file = f"{start}.dot"
    write_dot(start, nodes, edges, output_file)

    print(f"Wrote {output_file}")
    print(f"Total nodes: {len(nodes)}")
    print(f"Total edges: {len(edges)}")