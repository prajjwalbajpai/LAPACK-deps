# LAPACK-deps
Manage and inspect LAPACK routine dependencies (build a dependency graph, topo-sort it, and export per-routine .dot graphs for visualization).

Repository layout
```bash
.
├── deps_finder.py        # main helper: extract subgraph for a routine → .dot
├── script/               # helpers that build/validate the graph + topo order
└── output/               # generated artifacts (graphs, orders, lists, diagnostics)
```

## Dependency Finder

`deps_finder.py` extracts the dependency subgraph starting from a single LAPACK routine name (a root) using the full graph stored at `output/graph.json`. It writes a `.dot` file named `<routine>.dot` you can use visualisation tools like [GraphViz](https://dreampuf.github.io/GraphvizOnline/) to see the dependency graph.

### How to run it
```bash
python deps_finder.py <dependency_name>
```

## Scripts

1. `routine-names-blas.py`: Produces `output/routines_blas.txt` by listing BLAS routine filenames found in a local LAPACK/BLAS source tree.

2. `routine-names.py`: Produces `output/routines.txt` by listing LAPACK routine filenames found in a local LAPACK source tree.

3. `parse-dep.py`: Parses LAPACK source files to build the dependency mapping and writes `output/graph.json` (and a BLAS-specific `output/graph_blas.json`). It relies on the `output/routines.txt` & `output/routines_blas.txt` lists for known names.

4. `topo_sort.py`: Loads `output/graph.json`, runs a deterministic Kahn-style topo sort, writes the working order to `output/topo_order.txt`, and writes cycle information (SCCs) to `output/cycles.txt` if cycles exist.
  
5. `check.py`: Loads `output/graph.json` and `output/topo_order.txt` and reports (and writes) dependency problems: dependencies that appear after their dependents in the topo order (`output/wrong_deps.txt`) and dependencies referenced but missing from the topo list (`output/missing_deps.txt`).

6. `segregate.py`: Takes the topological order (`output/topo_order.txt`) and splits routines into precision/complexity groups (e.g. `SINGLE_PRECISION.txt`, `DOUBLE_PRECISION.txt`, `SINGLE_PRECISION_COMPLEX.txt`, `DOUBLE_PRECISION_COMPLEX.txt`, `OTHERS.txt`) based on routine name prefixes.


## Outputs

1. `graph.json`: JSON mapping routine -> [dependencies] for LAPACK routines.
2. `graph_blas.json`: Same as graph.json but for BLAS routines.
3. `routines.txt`: Plain list of LAPACK routine names discovered in the local source tree.
4. `routines_blas.txt`: Plain list of BLAS routine names discovered in the local BLAS source tree.
5. `topo_order.txt`: Newline-separated topological build/working order produced by `topo_sort.py`.
6. `cycles.txt`: If cycles exist, this file groups strongly-connected components (SCCs) that form cycles; otherwise contains “No cycles detected.”
7. `wrong_deps.txt`: Dependency pairs where a dependency appears after the dependent in the topo order (i.e., ordering violations).
8. `missing_deps.txt`: Dependency names referenced in the graph but missing from the topo list / known routines.

