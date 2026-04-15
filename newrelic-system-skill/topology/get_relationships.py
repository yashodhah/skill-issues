"""
topology/get_relationships.py

Return the direct dependencies of a New Relic entity.

Given an entity guid, this script returns two arrays: "calls"
(downstream services this entity calls) and "called_by" (upstream
services that call this entity). Each entry includes health
information (alertSeverity) so an agent can immediately see which
neighbours are unhealthy.

NerdGraph query used:

    {
      actor {
        entity(guid: "<GUID>") {
          relatedEntities(filter: {relationshipTypes: {include: CALLS}}) {
            results {
              source { entity { guid name entityType alertSeverity } }
              target { entity { guid name entityType alertSeverity } }
              type
            }
          }
        }
      }
    }

Usage:
    python topology/get_relationships.py --entity-guid <GUID>
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
from common.nerdgraph import nerdgraph_query  # noqa: E402


_RELATIONSHIPS_QUERY = """
{
  actor {
    entity(guid: "%s") {
      relatedEntities(filter: {relationshipTypes: {include: CALLS}}) {
        results {
          source {
            entity {
              guid
              name
              entityType
              alertSeverity
            }
          }
          target {
            entity {
              guid
              name
              entityType
              alertSeverity
            }
          }
          type
        }
      }
    }
  }
}
"""


def _shape(entity):
    """Normalise a relationship endpoint to a small dict."""
    if not entity:
        return None
    return {
        "guid": entity.get("guid"),
        "name": entity.get("name"),
        "entityType": entity.get("entityType"),
        "alertSeverity": entity.get("alertSeverity"),
    }


def get_relationships(entity_guid):
    """
    Fetch the direct CALLS relationships for an entity.

    Parameters
    ----------
    entity_guid : str
        The New Relic entity guid.

    Returns
    -------
    dict
        {"calls": [...], "called_by": [...]}
        "calls" are outbound (this entity -> target).
        "called_by" are inbound (source -> this entity).
    """
    safe_guid = entity_guid.replace('"', '\\"')
    query = _RELATIONSHIPS_QUERY % safe_guid
    data = nerdgraph_query(query)

    try:
        results = data["actor"]["entity"]["relatedEntities"]["results"]
    except (KeyError, TypeError):
        results = []

    calls = []
    called_by = []
    for rel in results or []:
        source_entity = (rel.get("source") or {}).get("entity")
        target_entity = (rel.get("target") or {}).get("entity")

        source_guid = (source_entity or {}).get("guid")
        target_guid = (target_entity or {}).get("guid")

        # Outbound: this entity is the source, target is the dependency.
        if source_guid == entity_guid and target_entity is not None:
            shaped = _shape(target_entity)
            if shaped is not None:
                calls.append(shaped)

        # Inbound: this entity is the target, source is the caller.
        if target_guid == entity_guid and source_entity is not None:
            shaped = _shape(source_entity)
            if shaped is not None:
                called_by.append(shaped)

    return {"calls": calls, "called_by": called_by}


def main():
    check_env()
    parser = argparse.ArgumentParser(
        description="Return direct upstream/downstream dependencies for an entity."
    )
    parser.add_argument("--entity-guid", required=True)
    args = parser.parse_args()

    result = get_relationships(args.entity_guid)
    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
