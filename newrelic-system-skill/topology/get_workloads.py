"""
topology/get_workloads.py

List New Relic Workloads in the account and return the entities they
contain. Workloads are user-curated logical groupings of services
(e.g. "Checkout Platform"), which is often the most honest source of
truth for "what is this team responsible for".

NerdGraph query used:

    {
      actor {
        account(id: <ACCOUNT_ID>) {
          workload {
            collections {
              guid
              name
              entities { guid }
            }
          }
        }
      }
    }

Usage:
    python topology/get_workloads.py
    python topology/get_workloads.py --workload-name "Checkout Platform"
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


_WORKLOADS_QUERY = """
{
  actor {
    account(id: %s) {
      workload {
        collections {
          guid
          name
          entities {
            guid
          }
        }
      }
    }
  }
}
"""


def get_workloads(account_id, workload_name=None):
    """
    Return the list of workloads in an account.

    Parameters
    ----------
    account_id : str
        The numeric account id, as a string.
    workload_name : str, optional
        If provided, only workloads whose name matches exactly are
        returned.

    Returns
    -------
    list of dict
        Each element: {"guid", "name", "entity_guids": [...]}.
    """
    query = _WORKLOADS_QUERY % account_id
    data = nerdgraph_query(query)

    try:
        collections = data["actor"]["account"]["workload"]["collections"]
    except (KeyError, TypeError):
        collections = []

    results = []
    for workload in collections or []:
        if workload_name is not None and workload.get("name") != workload_name:
            continue
        entity_guids = [e.get("guid") for e in workload.get("entities", []) if e.get("guid")]
        results.append(
            {
                "guid": workload.get("guid"),
                "name": workload.get("name"),
                "entity_guids": entity_guids,
            }
        )

    return results


def main():
    _api_key, account_id = check_env()
    parser = argparse.ArgumentParser(
        description="List New Relic workloads and their entity members."
    )
    parser.add_argument("--workload-name", default=None)
    args = parser.parse_args()

    workloads = get_workloads(account_id, args.workload_name)
    print(json.dumps(workloads, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
