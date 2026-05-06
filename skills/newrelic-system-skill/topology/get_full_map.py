"""
topology/get_full_map.py

Recursively walk CALLS relationships from a starting entity to build
a full dependency graph up to a configurable depth. Nodes are
deduplicated by guid, so the result is suitable for visualisation or
impact-radius analysis.

Uses the same NerdGraph relationships API as get_relationships.py,
just applied breadth-first.

Usage:
    python topology/get_full_map.py --entity-guid <GUID> --depth 3
"""

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from common.config import check_env  # noqa: E402
from topology.get_relationships import get_relationships  # noqa: E402


def get_full_map(root_guid, depth=3):
    """
    Build a dependency graph starting from root_guid.

    Parameters
    ----------
    root_guid : str
        The entity guid at the centre of the graph.
    depth : int
        Maximum number of hops to walk outward. Must be >= 1.

    Returns
    -------
    dict
        {
          "root": "<root_guid>",
          "depth": <depth>,
          "nodes": [...unique entity summaries...],
          "edges": [{"from", "to", "type"}]
        }
    """
    if depth < 1:
        depth = 1

    nodes_by_guid = {}
    edges = []
    seen_edges = set()
    visited = set()

    # BFS: each frontier item is (guid, current_depth).
    frontier = [(root_guid, 0)]

    while frontier:
        next_frontier = []
        for guid, current_depth in frontier:
            if guid in visited:
                continue
            visited.add(guid)

            if current_depth >= depth:
                continue

            try:
                rels = get_relationships(guid)
            except Exception as exc:
                print(
                    "WARN: failed to expand guid={0}: {1}".format(guid, exc),
                    file=sys.stderr,
                )
                continue

            for neighbour in rels.get("calls", []):
                n_guid = neighbour.get("guid")
                if not n_guid:
                    continue
                nodes_by_guid[n_guid] = neighbour
                edge_key = (guid, n_guid, "CALLS")
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges.append({"from": guid, "to": n_guid, "type": "CALLS"})
                if n_guid not in visited:
                    next_frontier.append((n_guid, current_depth + 1))

            for neighbour in rels.get("called_by", []):
                n_guid = neighbour.get("guid")
                if not n_guid:
                    continue
                nodes_by_guid[n_guid] = neighbour
                edge_key = (n_guid, guid, "CALLS")
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges.append({"from": n_guid, "to": guid, "type": "CALLS"})
                if n_guid not in visited:
                    next_frontier.append((n_guid, current_depth + 1))

        frontier = next_frontier

    # The root itself should appear in the node list even if nothing
    # references it. We don't have its full metadata here, so we record
    # a minimal stub unless it was already added as a neighbour.
    if root_guid not in nodes_by_guid:
        nodes_by_guid[root_guid] = {
            "guid": root_guid,
            "name": None,
            "entityType": None,
            "alertSeverity": None,
        }

    return {
        "root": root_guid,
        "depth": depth,
        "nodes": list(nodes_by_guid.values()),
        "edges": edges,
    }


def main():
    check_env()
    parser = argparse.ArgumentParser(
        description="Recursively build a dependency graph from an entity."
    )
    parser.add_argument("--entity-guid", required=True)
    parser.add_argument("--depth", type=int, default=3)
    args = parser.parse_args()

    result = get_full_map(args.entity_guid, args.depth)
    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
