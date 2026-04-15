"""
health/get_open_alerts.py

Return currently open AI-correlated incidents (issues) for the
account, optionally filtered to only those affecting a specific
entity.

NerdGraph query used:

    {
      actor {
        account(id: <ACCOUNT_ID>) {
          aiIssues {
            issues(filter: {states: ACTIVATED}) {
              issues {
                issueId title priority state createdAt entityGuids
              }
            }
          }
        }
      }
    }

Usage:
    python health/get_open_alerts.py
    python health/get_open_alerts.py --entity-guid <GUID>
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


_OPEN_ISSUES_QUERY = """
{
  actor {
    account(id: %s) {
      aiIssues {
        issues(filter: {states: ACTIVATED}) {
          issues {
            issueId
            title
            priority
            state
            createdAt
            entityGuids
          }
        }
      }
    }
  }
}
"""


def get_open_alerts(account_id, entity_guid=None):
    """
    Return the currently-open issues for an account, optionally
    restricted to those affecting a specific entity.

    Parameters
    ----------
    account_id : str
        Numeric account id, as a string.
    entity_guid : str, optional
        If supplied, only issues that list this guid in entityGuids
        are returned.

    Returns
    -------
    list of dict
        [{ "issueId", "title", "priority", "state", "entityGuids", "openedAt" }]
    """
    data = nerdgraph_query(_OPEN_ISSUES_QUERY % account_id)

    try:
        issues = data["actor"]["account"]["aiIssues"]["issues"]["issues"]
    except (KeyError, TypeError):
        issues = []

    out = []
    for issue in issues or []:
        guids = issue.get("entityGuids") or []
        if isinstance(guids, str):
            # Some account types return a single string; normalise to a list.
            guids = [guids]

        if entity_guid is not None and entity_guid not in guids:
            continue

        titles = issue.get("title")
        # title may be a list of strings - keep as-is but also expose
        # the joined form for convenience.
        if isinstance(titles, list):
            title_value = titles
        else:
            title_value = titles

        out.append(
            {
                "issueId": issue.get("issueId"),
                "title": title_value,
                "priority": issue.get("priority"),
                "state": issue.get("state"),
                "entityGuids": guids,
                "openedAt": issue.get("createdAt"),
            }
        )

    return out


def main():
    _api_key, account_id = check_env()
    parser = argparse.ArgumentParser(
        description="Return currently open alert issues."
    )
    parser.add_argument("--entity-guid", default=None)
    args = parser.parse_args()

    alerts = get_open_alerts(account_id, args.entity_guid)
    print(json.dumps(alerts, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
