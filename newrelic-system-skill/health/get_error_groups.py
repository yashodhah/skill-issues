"""
health/get_error_groups.py

Return the top error groups (fingerprinted exception classes) for a
service over a recent time window.

NRQL used:

    SELECT count(*)
    FROM ErrorTrace
    WHERE entityGuid = '<GUID>'
    FACET error.class, error.message
    SINCE <SINCE>
    LIMIT 20

Usage:
    python health/get_error_groups.py --entity-guid <GUID>
    python health/get_error_groups.py --entity-guid <GUID> --since "1 hour ago"
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


def get_error_groups(entity_guid, account_id, since="1 hour ago"):
    """
    Return the top error groups for an entity.

    Parameters
    ----------
    entity_guid : str
    account_id : str
    since : str
        NRQL SINCE clause, e.g. "1 hour ago".

    Returns
    -------
    list of dict
        [{ "error_class", "error_message", "count" }] sorted by count
        descending.
    """
    safe_guid = entity_guid.replace("'", "\\'")
    safe_since = since.replace("'", "\\'")
    nrql = (
        "SELECT count(*) FROM ErrorTrace "
        "WHERE entityGuid = '{0}' "
        "FACET error.class, error.message "
        "SINCE {1} LIMIT 20"
    ).format(safe_guid, safe_since)

    escaped_nrql = nrql.replace("\\", "\\\\").replace('"', '\\"')
    data = nerdgraph_query(_NRQL_QUERY % (account_id, escaped_nrql))

    try:
        results = data["actor"]["account"]["nrql"]["results"] or []
    except (KeyError, TypeError):
        results = []

    out = []
    for row in results:
        # FACET rows come back as either a "facet" array or individual
        # keyed values depending on server version; handle both shapes.
        facet = row.get("facet")
        error_class = None
        error_message = None
        if isinstance(facet, list):
            if len(facet) > 0:
                error_class = facet[0]
            if len(facet) > 1:
                error_message = facet[1]
        else:
            error_class = row.get("error.class")
            error_message = row.get("error.message")

        count = row.get("count") or 0
        out.append(
            {
                "error_class": error_class,
                "error_message": error_message,
                "count": count,
            }
        )

    out.sort(key=lambda x: x["count"] or 0, reverse=True)
    return out


def main():
    _api_key, account_id = check_env()
    parser = argparse.ArgumentParser(
        description="Return top error groups for a service."
    )
    parser.add_argument("--entity-guid", required=True)
    parser.add_argument("--since", default="1 hour ago")
    args = parser.parse_args()

    groups = get_error_groups(args.entity_guid, account_id, args.since)
    print(json.dumps(groups, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
