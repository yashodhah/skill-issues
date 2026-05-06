"""
query/nrql.py

Execute an arbitrary NRQL query against a New Relic account and
return the raw results. This is the low-level escape hatch for
agents or humans that need to run a one-off query that isn't covered
by a purpose-built script.

NerdGraph query used:

    {
      actor {
        account(id: <ACCOUNT_ID>) {
          nrql(query: "<NRQL>") {
            results
          }
        }
      }
    }

Usage:
    python query/nrql.py --query "SELECT count(*) FROM Transaction SINCE 1 hour ago"
    python query/nrql.py --query "..." --account-id 1234567
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


def run_nrql(nrql, account_id):
    """
    Execute an NRQL query and return the raw results array.

    Parameters
    ----------
    nrql : str
        The NRQL query string. Do NOT wrap it in quotes - this
        function handles escaping.
    account_id : str
        Numeric account id, as a string.

    Returns
    -------
    dict
        { "query": <original nrql>, "results": [...] }
    """
    escaped = nrql.replace("\\", "\\\\").replace('"', '\\"')
    data = nerdgraph_query(_NRQL_QUERY % (account_id, escaped))
    try:
        results = data["actor"]["account"]["nrql"]["results"] or []
    except (KeyError, TypeError):
        results = []
    return {"query": nrql, "results": results}


def main():
    _api_key, env_account_id = check_env()
    parser = argparse.ArgumentParser(
        description="Execute an arbitrary NRQL query."
    )
    parser.add_argument("--query", required=True)
    parser.add_argument("--account-id", default=None)
    args = parser.parse_args()

    account_id = args.account_id or env_account_id
    result = run_nrql(args.query, account_id)
    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
