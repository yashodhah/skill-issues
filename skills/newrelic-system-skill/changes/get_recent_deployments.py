"""
changes/get_recent_deployments.py

Return recent deployments recorded against a New Relic entity via the
change tracking API. Deployments are a critical input for "did this
deploy break anything?" workflows.

NerdGraph query used:

    {
      actor {
        entity(guid: "<GUID>") {
          deploymentSearch(filter: {timeWindow: {startTime: <MS>, endTime: <MS>}}) {
            results {
              version
              timestamp
              changelog
              user
              entityGuid
            }
          }
        }
      }
    }

Usage:
    python changes/get_recent_deployments.py --entity-guid <GUID>
    python changes/get_recent_deployments.py --entity-guid <GUID> --since "7 days ago"
"""

import argparse
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from common.config import check_env  # noqa: E402
from common.nerdgraph import nerdgraph_query  # noqa: E402


_DEPLOYMENTS_QUERY = """
{
  actor {
    entity(guid: "%s") {
      deploymentSearch(filter: {timeWindow: {startTime: %d, endTime: %d}}) {
        results {
          version
          timestamp
          changelog
          user
          entityGuid
        }
      }
    }
  }
}
"""


# Simple human-duration parser for common "N units ago" strings.
_UNITS_MS = {
    "second": 1000,
    "seconds": 1000,
    "minute": 60 * 1000,
    "minutes": 60 * 1000,
    "hour": 60 * 60 * 1000,
    "hours": 60 * 60 * 1000,
    "day": 24 * 60 * 60 * 1000,
    "days": 24 * 60 * 60 * 1000,
    "week": 7 * 24 * 60 * 60 * 1000,
    "weeks": 7 * 24 * 60 * 60 * 1000,
}


def parse_since_to_start_ms(since):
    """
    Convert a "N units ago" string to an epoch-ms start time.

    Defaults to 24 hours ago if the string can't be parsed.
    """
    now_ms = int(time.time() * 1000)
    parts = since.strip().split()
    if len(parts) >= 2:
        try:
            amount = int(parts[0])
            unit = parts[1].lower()
            unit_ms = _UNITS_MS.get(unit)
            if unit_ms is not None:
                return now_ms - (amount * unit_ms)
        except ValueError:
            pass
    # Fallback: 24 hours.
    return now_ms - 24 * 60 * 60 * 1000


def get_recent_deployments(entity_guid, since="24 hours ago"):
    """
    Return deployment records for an entity.

    Parameters
    ----------
    entity_guid : str
    since : str
        "N units ago" format. Defaults to "24 hours ago".

    Returns
    -------
    list of dict
        [{ "version", "timestamp", "changelog", "user", "entityGuid" }]
        sorted newest-first.
    """
    safe_guid = entity_guid.replace('"', '\\"')
    start_ms = parse_since_to_start_ms(since)
    end_ms = int(time.time() * 1000)

    query = _DEPLOYMENTS_QUERY % (safe_guid, start_ms, end_ms)
    data = nerdgraph_query(query)

    try:
        results = data["actor"]["entity"]["deploymentSearch"]["results"] or []
    except (KeyError, TypeError):
        results = []

    out = []
    for row in results:
        out.append(
            {
                "version": row.get("version"),
                "timestamp": row.get("timestamp"),
                "changelog": row.get("changelog"),
                "user": row.get("user"),
                "entityGuid": row.get("entityGuid"),
            }
        )

    out.sort(key=lambda x: x["timestamp"] or 0, reverse=True)
    return out


def main():
    check_env()
    parser = argparse.ArgumentParser(
        description="Return recent deployments for a New Relic entity."
    )
    parser.add_argument("--entity-guid", required=True)
    parser.add_argument("--since", default="24 hours ago")
    args = parser.parse_args()

    deployments = get_recent_deployments(args.entity_guid, args.since)
    print(json.dumps(deployments, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
