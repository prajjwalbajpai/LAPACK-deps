#!/usr/bin/env python3
import json
import pathlib
from typing import Dict, List, Tuple

INPUT_JSON = "output/graph.json"
INPUT_TOPO = "output/topo_order.txt"
OUTPUT_WRONG = "output/wrong_deps.txt"
OUTPUT_MISSING = "output/missing_deps.txt"

def load_graph(path: str) -> Dict[str, List[str]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    norm = {}
    for k, v in data.items():
        key = k.strip().lower()
        if v is None:
            norm[key] = []
        elif isinstance(v, list):
            norm[key] = [str(x).strip().lower() for x in v if str(x).strip()]
        elif isinstance(v, str):
            norm[key] = [v.strip().lower()]
        else:
            try:
                norm[key] = [str(x).strip().lower() for x in list(v)]
            except Exception:
                norm[key] = []
    return norm

def load_topo(path: str) -> List[str]:
    lines = pathlib.Path(path).read_text(encoding="utf-8").splitlines()
    topo = []
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#"):      # ignore comment blocks (SCC markers, etc.)
            continue
        topo.append(s.lower())
    return topo

def find_wrong_deps(graph: Dict[str, List[str]], topo: List[str]):
    pos = {name: i for i, name in enumerate(topo)}
    wrong: List[Tuple[str, str, int, int]] = []   # (dependent, dependency, pos_dep, pos_dependent)
    missing = set()  # dependencies referenced but not in topo

    for dependent in topo:
        deps = graph.get(dependent, [])
        for dep in deps:
            if dep not in pos:
                missing.add(dep)
                continue
            if pos[dep] > pos[dependent]:
                wrong.append((dependent, dep, pos[dep], pos[dependent]))

    return wrong, sorted(missing)

def main():
    graph = load_graph(INPUT_JSON)
    topo = load_topo(INPUT_TOPO)

    wrong, missing = find_wrong_deps(graph, topo)

    # Write wrong pairs
    with open(OUTPUT_WRONG, "w", encoding="utf-8") as f:
        f.write("# dependent -> dependency (pos_dep > pos_dependent)\n")
        for depd, dep, p_dep, p_depd in wrong:
            f.write(f"{depd} -> {dep}  (dep_pos={p_dep}, dependent_pos={p_depd})\n")

    # Write missing deps
    with open(OUTPUT_MISSING, "w", encoding="utf-8") as f:
        if not missing:
            f.write("No missing deps (all dependencies appear in topo list).\n")
        else:
            for m in missing:
                f.write(m + "\n")

    print(f"Total topo nodes checked: {len(topo)}")
    print(f"Wrong dependency **pairs** (dep appears after dependent): {len(wrong)}")
    print(f"Unique dependency names missing from topo: {len(missing)}")
    if wrong:
        print("Sample wrong deps (first 20):")
        for t in wrong[:20]:
            print(f"  {t[0]} -> {t[1]}  (dep_pos={t[2]}, dependent_pos={t[3]})")
    print(f"Wrote offending pairs to: {OUTPUT_WRONG}")
    print(f"Wrote missing dependency names to: {OUTPUT_MISSING}")

if __name__ == "__main__":
    main()
