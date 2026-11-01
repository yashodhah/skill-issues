"""
topology/get_entity.py

Resolve a service name to a New Relic entity.

Given a human-readable service name (for example "payment-service")
this script returns the New Relic entity that matches, including its
guid, name, entityType, accountId, and tags. The guid returned here
is the handle used by every other script in this skill.

NerdGraph query used:

    {
      actor {
        entitySearch(query: "name = '<SERVICE_NAME>'") {
          results {
            entities {
              guid name entityType accountId
              tags { key values }
            }
          }
        }
      }
    }

Usage:
    python topology/get_entity.py --service-name payment-service
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


_ENTITY_SEARCH_QUERY = """
{
  actor {
    entitySearch(query: "name = '%s'") {
      results {
        entities {
          guid
          name
          entityType
          accountId
          tags {
            key
            values
          }
        }
      }
    }
  }
}
"""


def get_entity(service_name):
    """
    Look up an entity by exact name match.

    Parameters
    ----------
    service_name : str
        The name of the service as it appears in New Relic.

    Returns
    -------
    dict or None
        The first matching entity with keys: guid, name, entityType,
        accountId, tags. Returns None if no entity matched.
    """
    # entitySearch uses NRQL-style single-quoted string literals, so
    # we defend against a stray apostrophe in the service name.
    safe_name = service_name.replace("'", "\\'")
    query = _ENTITY_SEARCH_QUERY % safe_name

    data = nerdgraph_query(query)
    try:
        entities = data["actor"]["entitySearch"]["results"]["entities"]
    except (KeyError, TypeError):
        return None

    if not entities:
        return None

    entity = entities[0]
    return {
        "guid": entity.get("guid"),
        "name": entity.get("name"),
        "entityType": entity.get("entityType"),
        "accountId": entity.get("accountId"),
        "tags": entity.get("tags", []),
    }


def main():
    check_env()
    parser = argparse.ArgumentParser(
        description="Resolve a New Relic entity by service name."
    )
    parser.add_argument("--service-name", required=True)
    args = parser.parse_args()

    entity = get_entity(args.service_name)
    if entity is None:
        print(
            "ERROR: No entity found for service-name='{0}'".format(
                args.service_name
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    print(json.dumps(entity, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
