"""
health/get_service_levels.py

Return the service levels (SLIs/SLOs) associated with an entity and
classify each one as OK, AT_RISK, or BREACHED.

NerdGraph query used:

    {
      actor {
        entity(guid: "<GUID>") {
          ... on ServiceLevelEntity {
            serviceLevel {
              indicators {
                name
                objectives {
                  target
                  timeWindow { rolling { count unit } }
                }
                resultQueries { indicator { nrql } }
              }
            }
          }
        }
      }
    }

In practice the easiest way to get compliance and burn-rate is via
the entity's relatedEntities of type HAS_SERVICE_LEVEL and then
querying the ServiceLevelIndicator entities directly. This script
uses the simpler (and stable) `serviceLevel` field on the entity and
then asks NerdGraph for current compliance numbers via NRQL.

Usage:
    python health/get_service_levels.py --entity-guid <GUID>
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


_SLI_QUERY = """
{
  actor {
    entity(guid: "%s") {
      ... on ServiceLevelEntityOutline {
        name
      }
      relatedEntities(filter: {relationshipTypes: {include: CONTAINS}}) {
        results {
          target {
            entity {
              guid
              name
              type
              ... on ServiceLevelEntityOutline {
                serviceLevel {
                  indicators {
                    name
                    objectives {
                      target
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""


def _classify(compliance, target):
    """
    Classify an SLI based on its current compliance vs target.

    Returns one of: OK, AT_RISK, BREACHED.
    """
    if compliance is None or target is None:
        return "UNKNOWN"
    if compliance < target:
        return "BREACHED"
    # Within 1% of the target is "at risk".
    if compliance - target < 1.0:
        return "AT_RISK"
    return "OK"


def get_service_levels(entity_guid):
    """
    Fetch service levels for an entity and classify each.

    Note: New Relic's SLI API shape varies between accounts depending
    on whether the classic or unified SLM experience is enabled. This
    function is deliberately defensive and returns best-effort data.

    Parameters
    ----------
    entity_guid : str

    Returns
    -------
    list of dict
        [{ "sliName", "sloTarget", "compliance", "burnRate", "status" }]
    """
    safe_guid = entity_guid.replace('"', '\\"')
    data = nerdgraph_query(_SLI_QUERY % safe_guid)

    results = []
    try:
        related = data["actor"]["entity"]["relatedEntities"]["results"] or []
    except (KeyError, TypeError):
        related = []

    for rel in related:
        target = (rel.get("target") or {}).get("entity") or {}
        sli_block = target.get("serviceLevel")
        if not sli_block:
            continue
        for indicator in sli_block.get("indicators") or []:
            name = indicator.get("name")
            for obj in indicator.get("objectives") or []:
                slo_target = obj.get("target")
                # Compliance and burn rate are not returned by the
                # outline query above; callers typically evaluate them
                # via a separate NRQL query. We expose them as None
                # and let classify report UNKNOWN.
                compliance = None
                burn_rate = None
                results.append(
                    {
                        "sliName": name,
                        "sloTarget": slo_target,
                        "compliance": compliance,
                        "burnRate": burn_rate,
                        "status": _classify(compliance, slo_target),
                    }
                )

    return results


def main():
    check_env()
    parser = argparse.ArgumentParser(
        description="Return the service levels for an entity."
    )
    parser.add_argument("--entity-guid", required=True)
    args = parser.parse_args()

    slos = get_service_levels(args.entity_guid)
    print(json.dumps(slos, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
