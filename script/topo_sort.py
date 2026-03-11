#!/usr/bin/env python3
"""
Topo-sort a dependency graph stored as JSON (routine -> list of dependencies)
and write a newline-separated working order to a text file.

Cycles (if any) are written to CYCLES_TXT where different cycles (SCCs)
are separated and labelled.

Hardcoded paths:
  INPUT_JSON = "output/graph.json"
  OUTPUT_TXT = "output/topo_order.txt"
  CYCLES_TXT = "output/cycles.txt"
"""

import json
from collections import defaultdict
import heapq
from typing import Dict, List, Set

# ------------------ hardcoded paths ------------------
INPUT_JSON = "output/graph.json"
OUTPUT_TXT = "output/topo_order.txt"
CYCLES_TXT = "output/cycles.txt"
# -----------------------------------------------------


def load_graph(path: str) -> Dict[str, List[str]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Normalize values: ensure each value is a list
    norm: Dict[str, List[str]] = {}
    for k, v in data.items():
        if v is None:
            norm[k] = []
        elif isinstance(v, list):
            norm[k] = v
        elif isinstance(v, str):
            norm[k] = [v]
        else:
            # fallback: try to coerce iterables to list
            try:
                norm[k] = list(v)
            except Exception:
                norm[k] = []
    return norm


def build_graph(deps_map: Dict[str, List[str]]):
    """
    Input map: node -> [dependencies]
    We want edges dependency -> node (so dependencies come before node)
    Returns adjacency list and indegree dict
    """
    adj = defaultdict(list)      # dep -> [nodes that depend on dep]
    indeg = defaultdict(int)     # node -> indegree
    nodes: Set[str] = set()

    # collect nodes and referenced nodes
    for node, deps in deps_map.items():
        nodes.add(node)
        for d in deps:
            nodes.add(d)

    # initialize indegrees
    for n in nodes:
        indeg[n] = 0

    # build edges (dep -> node)
    for node, deps in deps_map.items():
        for d in deps:
            adj[d].append(node)
            indeg[node] += 1

    return adj, indeg, nodes


def kahn_topo(adj, indeg, nodes):
    """
    Kahn's algorithm using a min-heap for deterministic order.
    Returns (order_list, remaining_with_indegree) where remaining_with_indegree is a list of nodes
    that still have indegree>0 (cycle participants) if cycle exists.
    """
    heap = [n for n in nodes if indeg[n] == 0]
    heapq.heapify(heap)

    order = []
    while heap:
        n = heapq.heappop(heap)
        order.append(n)
        for nbr in adj.get(n, []):
            indeg[nbr] -= 1
            if indeg[nbr] == 0:
                heapq.heappush(heap, nbr)

    remaining = [n for n in nodes if indeg[n] > 0]
    return order, remaining


# --- Tarjan's algorithm to find SCCs ---
def tarjan_scc(nodes: Set[str], graph: Dict[str, List[str]]) -> List[List[str]]:
    """
    nodes: set of nodes to consider
    graph: adjacency list mapping node -> [neighbour nodes]
    returns list of SCCs (each SCC is a list of nodes)
    """
    index = 0
    indices: Dict[str, int] = {}
    lowlink: Dict[str, int] = {}
    stack: List[str] = []
    onstack: Set[str] = set()
    sccs: List[List[str]] = []

    def strongconnect(v: str):
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        onstack.add(v)

        for w in graph.get(v, []):
            if w not in indices:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in onstack:
                lowlink[v] = min(lowlink[v], indices[w])

        # If v is a root node, pop the stack and generate an SCC
        if lowlink[v] == indices[v]:
            scc = []
            while True:
                w = stack.pop()
                onstack.remove(w)
                scc.append(w)
                if w == v:
                    break
            sccs.append(scc)

    for v in nodes:
        if v not in indices:
            strongconnect(v)

    return sccs


def find_cycle_groups(remaining: List[str], deps_map: Dict[str, List[str]]) -> List[List[str]]:
    """
    Given the list of nodes that still have indegree>0 (i.e. involved in cycles),
    build a subgraph restricted to those nodes using the original direction (node -> deps)
    and find SCCs. Return only SCCs that are real cycles (size>1 or self-loop).
    """
    rem_set = set(remaining)
    # build subgraph in the direction node -> dependency (this is the original deps_map direction)
    subgraph: Dict[str, List[str]] = {}
    for n in rem_set:
        subgraph[n] = [d for d in deps_map.get(n, []) if d in rem_set]

    sccs = tarjan_scc(rem_set, subgraph)
    cycles = []
    for scc in sccs:
        if len(scc) > 1:
            cycles.append(scc)
        elif len(scc) == 1:
            v = scc[0]
            # self-loop check
            if v in subgraph.get(v, []):
                cycles.append(scc)
    return cycles


def write_order(path: str, order: List[str]):
    with open(path, "w", encoding="utf-8") as f:
        for name in order:
            f.write(f"{name}\n")


def write_cycles_grouped(path: str, cycles: List[List[str]]):
    with open(path, "w", encoding="utf-8") as f:
        if not cycles:
            f.write("No cycles detected.\n")
            return
        f.write(f"{len(cycles)} cycle(s) detected. Each cycle is listed below.\n\n")
        for i, cyc in enumerate(cycles, start=1):
            f.write(f"=== Cycle {i} (size={len(cyc)}) ===\n")
            # write nodes in cycle in stable order
            for n in sorted(cyc):
                f.write(n + "\n")
            f.write("\n")


def main():
    deps_map = load_graph(INPUT_JSON)
    adj, indeg, nodes = build_graph(deps_map)
    order, remaining = kahn_topo(adj, indeg, nodes)

    # write whatever order we got (even if partial)
    write_order(OUTPUT_TXT, order)

    if remaining:
        print(f"[WARN] Cycle detected: {len(remaining)} node(s) remain with indegree > 0.")
        # group remaining nodes into distinct cycles (SCCs)
        cycles = find_cycle_groups(remaining, deps_map)
        write_cycles_grouped(CYCLES_TXT, cycles)
        print(f"Partial order written to: {OUTPUT_TXT}")
        print(f"Cycle groups written to: {CYCLES_TXT}")
    else:
        # no cycles
        # clear cycles file or write a short note
        write_cycles_grouped(CYCLES_TXT, [])
        print(f"[OK] Topological order produced with {len(order)} nodes.")
        print(f"Order written to: {OUTPUT_TXT}")


if __name__ == "__main__":
    main()
