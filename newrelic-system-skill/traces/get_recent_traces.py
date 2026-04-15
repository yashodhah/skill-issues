"""
traces/get_recent_traces.py

Return the most recent distributed traces that touched a service,
sorted by duration so the slowest are first. This is the typical
starting point for "the service feels slow, where do I look?".

NRQL used:

    SELECT trace.id, duration.ms, name, timestamp
    FROM Span
    WHERE service.name = '<SERVICE_NAME>'
      AND span.kind = 'server'
    SINCE <SINCE>
    LIMIT 20

Usage:
    python traces/get_recent_traces.py --service-name payment-service
    python traces/get_recent_traces.py --service-name payment-service --since "15 minutes ago"
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


_NRQL_QUERY = """
{
  actor {
    account(id: %s) {
      nrql(query: "%s") {
        results
      }
    }
  }
}
"""


def get_recent_traces(service_name, account_id, since="30 minutes ago"):
    """
    Return recent root spans for a service.

    Parameters
    ----------
    service_name : str
    account_id : str
    since : str
        NRQL SINCE clause.

    Returns
    -------
    list of dict
        [{ "trace_id", "duration_ms", "name", "timestamp" }] sorted by
        duration descending.
    """
    safe_service = service_name.replace("'", "\\'")
    safe_since = since.replace("'", "\\'")
    nrql = (
        "SELECT trace.id, duration.ms, name, timestamp "
        "FROM Span "
        "WHERE service.name = '{0}' AND span.kind = 'server' "
        "SINCE {1} LIMIT 20"
    ).format(safe_service, safe_since)

    escaped_nrql = nrql.replace("\\", "\\\\").replace('"', '\\"')
    data = nerdgraph_query(_NRQL_QUERY % (account_id, escaped_nrql))

    try:
        results = data["actor"]["account"]["nrql"]["results"] or []
    except (KeyError, TypeError):
        results = []

    out = []
    for row in results:
        out.append(
            {
                "trace_id": row.get("trace.id"),
                "duration_ms": row.get("duration.ms"),
                "name": row.get("name"),
                "timestamp": row.get("timestamp"),
            }
        )

    out.sort(key=lambda x: x["duration_ms"] or 0, reverse=True)
    return out


def main():
    _api_key, account_id = check_env()
    parser = argparse.ArgumentParser(
        description="Return recent distributed traces for a service."
    )
    parser.add_argument("--service-name", required=True)
    parser.add_argument("--since", default="30 minutes ago")
    args = parser.parse_args()

    traces = get_recent_traces(args.service_name, account_id, args.since)
    print(json.dumps(traces, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
