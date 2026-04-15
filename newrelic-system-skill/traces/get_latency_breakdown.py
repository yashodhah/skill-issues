"""
traces/get_latency_breakdown.py

Return a per-span latency breakdown for a service. The output is a
sorted list showing which operation names are consuming the most
latency on average, and what their 95th percentile looks like. This
is the canonical way to answer "where is the time going?".

NRQL used:

    SELECT average(duration.ms), percentile(duration.ms, 95)
    FROM Span
    WHERE service.name = '<SERVICE_NAME>'
    FACET name
    SINCE <SINCE>
    LIMIT 20

Usage:
    python traces/get_latency_breakdown.py --service-name payment-service
    python traces/get_latency_breakdown.py --service-name payment-service --since "1 hour ago"
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


def get_latency_breakdown(service_name, account_id, since="30 minutes ago"):
    """
    Return a per-span latency breakdown for a service.

    Parameters
    ----------
    service_name : str
    account_id : str
    since : str
        NRQL SINCE clause. Default: "30 minutes ago".

    Returns
    -------
    list of dict
        [{ "span_name", "avg_duration_ms", "p95_duration_ms" }]
        sorted by avg_duration_ms descending.
    """
    safe_service = service_name.replace("'", "\\'")
    safe_since = since.replace("'", "\\'")
    nrql = (
        "SELECT average(duration.ms), percentile(duration.ms, 95) "
        "FROM Span "
        "WHERE service.name = '{0}' "
        "FACET name "
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
        # FACET rows can return either a "facet" array or an inline
        # "name" field depending on API version.
        facet = row.get("facet")
        if isinstance(facet, list) and facet:
            span_name = facet[0]
        else:
            span_name = row.get("name")

        avg_value = row.get("average.duration.ms")
        if avg_value is None:
            avg_value = row.get("average")

        p95_value = row.get("percentile.duration.ms")
        if p95_value is None:
            p95_value = row.get("percentile")
        # percentile() can return a dict like {"95": 123.4}
        if isinstance(p95_value, dict):
            if "95" in p95_value:
                p95_value = p95_value["95"]
            else:
                # Fall back to the first numeric value in the dict.
                numeric = [v for v in p95_value.values() if isinstance(v, (int, float))]
                p95_value = numeric[0] if numeric else None

        out.append(
            {
                "span_name": span_name,
                "avg_duration_ms": avg_value,
                "p95_duration_ms": p95_value,
            }
        )

    out.sort(key=lambda x: x["avg_duration_ms"] or 0, reverse=True)
    return out


def main():
    _api_key, account_id = check_env()
    parser = argparse.ArgumentParser(
        description="Return per-span latency breakdown for a service."
    )
    parser.add_argument("--service-name", required=True)
    parser.add_argument("--since", default="30 minutes ago")
    args = parser.parse_args()

    breakdown = get_latency_breakdown(args.service_name, account_id, args.since)
    print(json.dumps(breakdown, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
